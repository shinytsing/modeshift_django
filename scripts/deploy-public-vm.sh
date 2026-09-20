#!/usr/bin/env bash
# Deploy the immutable production image behind the public VMware Nginx entrypoint.
set -Eeuo pipefail

PROJECT_DIR="${QATOOLBOX_DIR:-$HOME/modeshift_django}"
COMPOSE_FILE="$PROJECT_DIR/docker/docker-compose.prod.yml"
ENV_FILE="$PROJECT_DIR/.env"
VM_ENV_FILE="$PROJECT_DIR/.env.vm"
APP_PORT="${APP_PORT:-8080}"

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "Production Compose file not found: $COMPOSE_FILE" >&2
  exit 1
fi
if [[ ! -f "$ENV_FILE" ]]; then
  if [[ -f "$VM_ENV_FILE" ]]; then
    echo "==> Reusing the existing VM environment as the production environment"
    umask 077
    cp "$VM_ENV_FILE" "$ENV_FILE"
  elif [[ -f "$PROJECT_DIR/.env.production" ]]; then
    echo "==> Reusing the existing production environment"
    umask 077
    cp "$PROJECT_DIR/.env.production" "$ENV_FILE"
  else
    echo "==> Creating a minimal production environment"
    umask 077
    {
      printf 'DJANGO_SECRET_KEY=%s\n' "$(openssl rand -hex 48)"
      printf 'ALLOWED_HOSTS=localhost,127.0.0.1,web,shenyiqing.xyz,www.shenyiqing.xyz\n'
    } > "$ENV_FILE"
  fi
fi

if [[ -n "${DEEPSEEK_API_KEY:-}" ]]; then
  umask 077
  env_tmp="$(mktemp "$PROJECT_DIR/.env.XXXXXX")"
  DEEPSEEK_API_KEY="$DEEPSEEK_API_KEY" awk '
    BEGIN { replaced = 0; value = ENVIRON["DEEPSEEK_API_KEY"] }
    /^DEEPSEEK_API_KEY=/ {
      if (!replaced) {
        print "DEEPSEEK_API_KEY=" value
        replaced = 1
      }
      next
    }
    { print }
    END {
      if (!replaced) print "DEEPSEEK_API_KEY=" value
    }
  ' "$ENV_FILE" > "$env_tmp"
  chmod 600 "$env_tmp"
  mv "$env_tmp" "$ENV_FILE"
  echo "==> DeepSeek API key supplied to public production environment"
fi
chmod 600 "$ENV_FILE"
if [[ -z "${QATOOLBOX_IMAGE:-}" ]]; then
  echo "QATOOLBOX_IMAGE is required." >&2
  exit 1
fi
if [[ -z "${GHCR_USERNAME:-}" || -z "${GHCR_PULL_TOKEN:-}" ]]; then
  echo "GHCR_USERNAME and GHCR_PULL_TOKEN are required." >&2
  exit 1
fi

SUDO=()
if [[ $EUID -ne 0 ]]; then
  SUDO=(sudo)
fi

docker_command=(docker)
if ! docker info >/dev/null 2>&1; then
  docker_command=("${SUDO[@]}" docker)
fi

compose() {
  "${docker_command[@]}" compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" "$@"
}

echo "==> Logging in to GitHub Container Registry"
printf '%s' "$GHCR_PULL_TOKEN" | "${docker_command[@]}" login ghcr.io \
  --username "$GHCR_USERNAME" --password-stdin >/dev/null

echo "==> Pulling production image $QATOOLBOX_IMAGE"
export QATOOLBOX_IMAGE
compose pull web

echo "==> Starting the public production stack on port $APP_PORT"
compose up -d --no-build db redis web nginx

for attempt in {1..30}; do
  if curl -fsS "http://127.0.0.1:${APP_PORT}/health/" >/dev/null; then
    break
  fi
  if [[ "$attempt" -eq 30 ]]; then
    echo "Public production stack did not become healthy." >&2
    compose logs --tail=100 web nginx >&2
    exit 1
  fi
  sleep 2
done

if [[ -n "${DEEPSEEK_API_KEY:-}" ]]; then
  if ! compose exec -T web sh -c 'test -n "${DEEPSEEK_API_KEY:-}"'; then
    echo "DeepSeek API key is missing inside the public web container." >&2
    exit 1
  fi
  compose exec -T web python - <<'PY'
import os
import requests

key = os.environ.get("DEEPSEEK_API_KEY", "")
print(f"DeepSeek key check: present={bool(key)}, length={len(key)}, prefix={key[:3]}")
try:
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 1,
        },
        timeout=10,
    )
    print(f"DeepSeek preflight HTTP status: {response.status_code}")
except Exception as exc:
    print(f"DeepSeek preflight error: {type(exc).__name__}: {exc}")
PY
  if ! compose exec -T web python -c \
    'from apps.tools.services.llm_service import DeepSeekService; raise SystemExit(0 if DeepSeekService().is_available() else 1)'; then
    echo "DeepSeek API key is present but the public web container cannot use DeepSeek." >&2
    exit 1
  fi
  echo "DeepSeek API connectivity verified in the public web container"
fi

echo "Public deployment succeeded: http://127.0.0.1:${APP_PORT}/health/"
