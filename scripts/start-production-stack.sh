#!/usr/bin/env bash
# Shared by systemd, manual starts and the GitHub deployment job.
set -Eeuo pipefail

PROJECT_DIR="${QATOOLBOX_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
ENV_FILE="$PROJECT_DIR/.env"
[[ -f "$ENV_FILE" ]] || { echo "Production environment missing: $ENV_FILE" >&2; exit 1; }
docker_command=(docker)
if [[ "${1:-}" != compose || "${2:-}" != config ]] && ! docker info >/dev/null 2>&1; then
  docker_command=(sudo -n docker)
fi
compose_args=(--project-name docker --project-directory "$PROJECT_DIR/docker" --env-file "$ENV_FILE" -f "$PROJECT_DIR/docker/docker-compose.prod.yml")
# Read only the enable flag, never source an env file as shell commands.
mcp_enabled=false
if python3 - "$ENV_FILE" <<'PY'
import pathlib
import sys

for line in pathlib.Path(sys.argv[1]).read_text().splitlines():
    key, sep, value = line.partition("=")
    if sep and key.strip() == "XHS_MCP_TOKEN":
        raise SystemExit(0 if value.strip().strip("\"'") else 1)
raise SystemExit(1)
PY
then
  mcp_enabled=true
  compose_args+=(-f "$PROJECT_DIR/docker/docker-compose.creator-watch.yml")
fi
compose() { "${docker_command[@]}" compose "${compose_args[@]}" "$@"; }
if [[ "${1:-start}" == "compose" ]]; then
  shift
  compose "$@"
  exit
fi
[[ "${1:-start}" == "start" ]] || { echo "Usage: $0 [start|compose <arguments>]" >&2; exit 2; }

exec 9>"$PROJECT_DIR/.production-start.lock"
flock -w 600 9
compose config --quiet
compose up -d --wait --wait-timeout 180 --no-build db redis
if [[ "$mcp_enabled" == true ]]; then
  compose up -d --wait --wait-timeout 180 --no-build xiaohongshu-mcp
fi
compose up -d --wait --wait-timeout 180 --no-build --no-deps web
# Nginx resolves the Web address at boot; recreate after Web is ready.
compose up -d --wait --wait-timeout 90 --no-build --no-deps --force-recreate nginx

# Retire the old, separately managed Worker before starting the only Beat.
legacy_ids="$("${docker_command[@]}" ps -aq --filter label=com.docker.compose.project=modeshift-worker --filter label=com.docker.compose.service=creator_watch)"
if [[ -n "$legacy_ids" ]]; then
  while IFS= read -r id; do
    "${docker_command[@]}" rm -f "$id"
  done <<< "$legacy_ids"
fi
compose up -d --wait --wait-timeout 180 --no-build --no-deps creator_watch
compose exec -T web sh -c 'celery -A config inspect ping --timeout 5' | grep -F pong
echo "Production stack is healthy; Web and Worker share the same Compose project and environment."
