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
SUDO=()
if [[ $EUID -ne 0 ]]; then
  SUDO=(sudo)
fi

docker_command=(docker)
if ! docker info >/dev/null 2>&1; then
  docker_command=("${SUDO[@]}" docker)
fi

echo "==> Remote deployment diagnostics"
uname -a
df -h "$PROJECT_DIR" /var/lib/docker 2>/dev/null || df -h "$PROJECT_DIR"
"${docker_command[@]}" info --format 'Docker server={{.ServerVersion}} storage={{.Driver}} root={{.DockerRootDir}}'

compose() {
  "${docker_command[@]}" compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" "$@"
}

export QATOOLBOX_IMAGE
if ! "${docker_command[@]}" image inspect "$QATOOLBOX_IMAGE" >/dev/null 2>&1; then
  echo "Locally built image is missing: $QATOOLBOX_IMAGE" >&2
  echo "This single-VM deployment intentionally does not pull from GHCR." >&2
  exit 1
fi
echo "==> Reusing locally built image $QATOOLBOX_IMAGE"

previous_image=""
if "${docker_command[@]}" container inspect modeshift_web >/dev/null 2>&1; then
  previous_image="$(${docker_command[@]} container inspect --format '{{.Config.Image}}' modeshift_web)"
  echo "==> Previous web image recorded for rollback: $previous_image"
fi

echo "==> Starting the public production stack on port $APP_PORT"
start_started_at=$(date +%s)
timeout --foreground 10m "${docker_command[@]}" compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d --no-build --force-recreate db redis web nginx
echo "==> Compose start finished in $(( $(date +%s) - start_started_at ))s"

if ! compose exec -T web sh -c 'test -f /app/media/vx.jpg'; then
  echo "==> Seeding missing default media asset media/vx.jpg"
  compose exec -T -u 0 web sh -c \
    'test -f /app/default_media/vx.jpg && cp /app/default_media/vx.jpg /app/media/vx.jpg && chmod 0644 /app/media/vx.jpg'
fi

if ! compose exec -T web sh -c 'test -f /app/staticfiles/img/wechat-contact.jpg'; then
  echo "==> Seeding missing static asset static/img/wechat-contact.jpg"
  compose exec -T -u 0 web sh -c \
    'test -f /app/default_static/img/wechat-contact.jpg && mkdir -p /app/staticfiles/img && cp /app/default_static/img/wechat-contact.jpg /app/staticfiles/img/wechat-contact.jpg && chmod 0644 /app/staticfiles/img/wechat-contact.jpg'
fi

if ! compose exec -T web sh -c 'test -f /app/staticfiles/img/vx.jpg'; then
  echo "==> Seeding missing static asset static/img/vx.jpg"
  compose exec -T -u 0 web sh -c \
    'test -f /app/default_static/img/vx.jpg && mkdir -p /app/staticfiles/img && cp /app/default_static/img/vx.jpg /app/staticfiles/img/vx.jpg && chmod 0644 /app/staticfiles/img/vx.jpg'
fi

for attempt in {1..30}; do
  if curl --noproxy '*' --connect-timeout 3 --max-time 10 -fsS "http://127.0.0.1:${APP_PORT}/health/" >/dev/null; then
    break
  fi
  if [[ "$attempt" -eq 30 ]]; then
    echo "Public production stack did not become healthy." >&2
    compose logs --tail=100 web nginx >&2
    if [[ -n "$previous_image" ]] && "${docker_command[@]}" image inspect "$previous_image" >/dev/null 2>&1; then
      echo "==> Rolling back to previous web image: $previous_image" >&2
      export QATOOLBOX_IMAGE="$previous_image"
      compose up -d --no-build web nginx >&2 || true
    fi
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

# Publish the release selection only after the application checks have passed.
# The boot unit previously pinned an old SHA in Environment=QATOOLBOX_IMAGE;
# an EnvironmentFile takes precedence over Environment= and survives reboot.
release_file="$PROJECT_DIR/.deployed-image.env"
release_tmp="$(mktemp "$PROJECT_DIR/.deployed-image.XXXXXX")"
printf 'QATOOLBOX_IMAGE=%s\n' "$QATOOLBOX_IMAGE" > "$release_tmp"
chmod 600 "$release_tmp"
mv "$release_tmp" "$release_file"

# Also keep ordinary docker compose invocations on the successful release.
env_tmp="$(mktemp "$PROJECT_DIR/.env.XXXXXX")"
awk -v image="$QATOOLBOX_IMAGE" '
  /^QATOOLBOX_IMAGE=/ { next }
  { print }
  END { print "QATOOLBOX_IMAGE=" image }
' "$ENV_FILE" > "$env_tmp"
chmod 600 "$env_tmp"
mv "$env_tmp" "$ENV_FILE"

if command -v systemctl >/dev/null && systemctl cat modeshift-django.service >/dev/null 2>&1; then
  boot_override="$(mktemp "$PROJECT_DIR/.boot-image.XXXXXX")"
  printf '[Service]\nEnvironmentFile="%s"\n' "$release_file" > "$boot_override"
  "${SUDO[@]}" install -D -m 0644 "$boot_override" \
    /etc/systemd/system/modeshift-django.service.d/90-deployed-image.conf
  "${SUDO[@]}" systemctl daemon-reload
  echo "==> Boot service will reuse successful image $QATOOLBOX_IMAGE"
fi

echo "Public deployment succeeded: http://127.0.0.1:${APP_PORT}/health/"
