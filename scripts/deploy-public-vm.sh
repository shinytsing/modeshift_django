#!/usr/bin/env bash
# Deploy the immutable production image behind the public VMware Nginx entrypoint.
set -Eeuo pipefail

PROJECT_DIR="${QATOOLBOX_DIR:-$HOME/modeshift_django}"
COMPOSE_FILE="$PROJECT_DIR/docker/docker-compose.prod.yml"
ENV_FILE="$PROJECT_DIR/.env"
APP_PORT="${APP_PORT:-8080}"

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "Production Compose file not found: $COMPOSE_FILE" >&2
  exit 1
fi
if [[ ! -f "$ENV_FILE" ]]; then
  echo "Production environment file not found: $ENV_FILE" >&2
  exit 1
fi
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
  if ! compose exec -T web python -c \
    'from apps.tools.services.llm_service import DeepSeekService; raise SystemExit(0 if DeepSeekService().is_available() else 1)'; then
    echo "DeepSeek API key is present but the public web container cannot use DeepSeek." >&2
    exit 1
  fi
  echo "DeepSeek API connectivity verified in the public web container"
fi

echo "Public deployment succeeded: http://127.0.0.1:${APP_PORT}/health/"
