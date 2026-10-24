#!/usr/bin/env bash
# Deploy the immutable production image behind the public VMware Nginx entrypoint.
set -Eeuo pipefail

PROJECT_DIR="${QATOOLBOX_DIR:-$HOME/modeshift_django}"
COMPOSE_FILE="$PROJECT_DIR/docker/docker-compose.prod.yml"
CREATOR_COMPOSE_FILE="$PROJECT_DIR/docker/docker-compose.creator-watch.yml"
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

# Persist the workflow's already verified SMTP settings for the web container.
# Values are never printed. Single quotes prevent Compose interpolation of `$`.
if [[ -n "${EMAIL_HOST:-}" && -n "${EMAIL_PORT:-}" && -n "${EMAIL_HOST_USER:-}" && -n "${EMAIL_HOST_PASSWORD:-}" && -n "${DEFAULT_FROM_EMAIL:-}" ]]; then
  python3 - "$ENV_FILE" <<'PY'
import os
import pathlib
import sys
import tempfile

path = pathlib.Path(sys.argv[1])
keys = ("EMAIL_HOST", "EMAIL_PORT", "EMAIL_USE_TLS", "EMAIL_HOST_USER", "EMAIL_HOST_PASSWORD", "DEFAULT_FROM_EMAIL")
values = {key: os.environ.get(key, "") for key in keys}
values["EMAIL_USE_TLS"] = values["EMAIL_USE_TLS"] or "true"
for key, value in values.items():
    if any(char in value for char in ("\n", "\r", "\0")):
        raise SystemExit(f"{key} contains a character unsupported by the deployment env file")
lines = [line for line in path.read_text().splitlines() if line.split("=", 1)[0] not in keys]
lines.extend(f"{key}='{value.replace(chr(39), chr(92) + chr(39))}'" for key, value in values.items())
with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, prefix=".env.mail.", delete=False) as handle:
    handle.write("\n".join(lines) + "\n")
    temporary = pathlib.Path(handle.name)
temporary.chmod(0o600)
temporary.replace(path)
PY
  echo "==> SMTP configuration supplied to public production environment"
fi
chmod 600 "$ENV_FILE"

creator_watch_mcp_enabled=false
if [[ -n "${XHS_MCP_TOKEN:-}" ]]; then
  if [[ ! -f "$CREATOR_COMPOSE_FILE" ]]; then
    echo "Creator-watch Compose overlay not found: $CREATOR_COMPOSE_FILE" >&2
    exit 1
  fi
  python3 - "$ENV_FILE" <<'PY'
import os
import pathlib
import sys
import tempfile

path = pathlib.Path(sys.argv[1])
token = os.environ["XHS_MCP_TOKEN"]
if any(char in token for char in ("\n", "\r", "\0", "'")):
    raise SystemExit("XHS_MCP_TOKEN contains a character unsupported by the deployment env file")
lines = [
    line for line in path.read_text().splitlines()
    if not line.startswith(("XHS_MCP_TOKEN=", "XHS_MCP_BASE_URL="))
]
lines.append(f"XHS_MCP_TOKEN='{token}'")
lines.append("XHS_MCP_BASE_URL=http://xiaohongshu-mcp:18060")
with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, prefix=".env.xhs.", delete=False) as handle:
    handle.write("\n".join(lines) + "\n")
    temporary = pathlib.Path(handle.name)
temporary.chmod(0o600)
temporary.replace(path)
PY
  creator_watch_mcp_enabled=true
  echo "==> Xiaohongshu MCP token supplied to public production environment"
fi

if [[ -z "${QATOOLBOX_IMAGE:-}" ]]; then
  echo "QATOOLBOX_IMAGE is required." >&2
  exit 1
fi
SUDO=()
if [[ $EUID -ne 0 ]]; then
  SUDO=(sudo -n)
fi

docker_command=(docker)
if ! docker info >/dev/null 2>&1; then
  docker_command=("${SUDO[@]}" docker)
fi

echo "==> Remote deployment diagnostics"
uname -a
df -h "$PROJECT_DIR" /var/lib/docker 2>/dev/null || df -h "$PROJECT_DIR"
"${docker_command[@]}" info --format 'Docker server={{.ServerVersion}} storage={{.Driver}} root={{.DockerRootDir}}'

compose_files=(-f "$COMPOSE_FILE")
if [[ "$creator_watch_mcp_enabled" == true ]]; then
  compose_files+=(-f "$CREATOR_COMPOSE_FILE")
fi
compose() {
  "${docker_command[@]}" compose --env-file "$ENV_FILE" "${compose_files[@]}" "$@"
}

export QATOOLBOX_IMAGE
if ! "${docker_command[@]}" image inspect "$QATOOLBOX_IMAGE" >/dev/null 2>&1; then
  echo "Locally built image is missing: $QATOOLBOX_IMAGE" >&2
  echo "This single-VM deployment intentionally does not pull from GHCR." >&2
  exit 1
fi
echo "==> Reusing locally built image $QATOOLBOX_IMAGE"
if [[ "$creator_watch_mcp_enabled" == true ]]; then
  xhs_image="${XHS_MCP_IMAGE:-modeshift-xhs-mcp:patched-7797fd3}"
  if ! "${docker_command[@]}" image inspect "$xhs_image" >/dev/null 2>&1; then
    echo "Patched Xiaohongshu MCP image is missing: $xhs_image" >&2
    echo "Build it from the pinned source and readiness patch before enabling XHS_MCP_TOKEN." >&2
    exit 1
  fi
  compose config --quiet
fi

previous_image=""
if "${docker_command[@]}" container inspect modeshift_web >/dev/null 2>&1; then
  previous_image="$(${docker_command[@]} container inspect --format '{{.Config.Image}}' modeshift_web)"
  echo "==> Previous web image recorded for rollback: $previous_image"
fi

echo "==> Starting the public production stack on port $APP_PORT"
start_started_at=$(date +%s)
# Preserve the persistent database and Redis containers during web releases.
# Recreating all four at once can race with the VM's boot/updater service and
# briefly remove healthy dependencies from the live application.
timeout --foreground 10m "${docker_command[@]}" compose --env-file "$ENV_FILE" "${compose_files[@]}" up -d --wait --wait-timeout 120 --no-build db redis
if [[ "$creator_watch_mcp_enabled" == true ]]; then
  timeout --foreground 10m "${docker_command[@]}" compose --env-file "$ENV_FILE" "${compose_files[@]}" up -d --wait --wait-timeout 120 --no-build xiaohongshu-mcp
fi
timeout --foreground 10m "${docker_command[@]}" compose --env-file "$ENV_FILE" "${compose_files[@]}" up -d --no-build --no-deps web nginx
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

# The persisted static volume masks collectstatic output baked into a new
# image. Refresh the archived resume reports from this release on every deploy.
echo "==> Syncing bundled resume reports into the persistent static volume"
compose exec -T -u 0 web sh -c \
  'test -f /app/static/resume-reports/gaotu-jmeter-20251127/index.html && \
   test -f /app/static/resume-reports/gaotu-locust-console-original.png && \
   mkdir -p /app/staticfiles/resume-reports && \
   cp -a /app/static/resume-reports/. /app/staticfiles/resume-reports/ && \
   chmod -R a+rX /app/staticfiles/resume-reports'

# Database migrations and the first Daphne boot can take several minutes on
# the single VMware host. Keep polling through the expected startup window so
# Nginx's temporary 502 during migration is not treated as a failed release.
for attempt in {1..180}; do
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

echo "==> Starting the daily creator-watch scheduler"
# A previous Compose project can leave the generated creator-watch container
# name behind. Remove only containers tagged as this service before recreating it.
creator_watch_ids=$(
  {
    "${docker_command[@]}" ps -aq --filter "label=com.docker.compose.service=creator_watch"
    "${docker_command[@]}" ps -aq --filter "name=creator_watch"
  } | sort -u
)
if [[ -n "$creator_watch_ids" ]]; then
  while IFS= read -r creator_watch_id; do
    [[ -z "$creator_watch_id" ]] || "${docker_command[@]}" rm -f "$creator_watch_id"
  done <<< "$creator_watch_ids"
fi
compose up -d --no-build --no-deps creator_watch
if [[ "$("${docker_command[@]}" inspect -f '{{.State.Running}}' "$(compose ps -q creator_watch)")" != "true" ]]; then
  echo "Creator-watch scheduler did not start." >&2
  compose logs --tail=50 creator_watch >&2
  exit 1
fi

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
  boot_compose_override="$HOME/.local/share/modeshift-updater/compose.success-image.override.yml"
  boot_exec="$(systemctl show modeshift-django.service --property=ExecStart --value)"
  boot_env="$(systemctl show modeshift-django.service --property=Environment --value)"
  if [[ -f "$boot_compose_override" && "$boot_exec" == *"$boot_compose_override"* && "$boot_env" != *QATOOLBOX_IMAGE=* ]]; then
    boot_image="$("${docker_command[@]}" compose --env-file "$ENV_FILE" \
      -f "$COMPOSE_FILE" -f "$boot_compose_override" config --format json |
      python3 -c 'import json,sys; print(json.load(sys.stdin)["services"]["web"]["image"])')"
    if [[ "$boot_image" != "$QATOOLBOX_IMAGE" ]]; then
      echo "Boot service resolves $boot_image instead of $QATOOLBOX_IMAGE" >&2
      exit 1
    fi
    echo "==> Boot service already resolves the successful image through its Compose override"
  else
    boot_override="$(mktemp "$PROJECT_DIR/.boot-image.XXXXXX")"
    printf '[Service]\nEnvironmentFile="%s"\n' "$release_file" > "$boot_override"
    boot_target=/etc/systemd/system/modeshift-django.service.d/90-deployed-image.conf
    if ! cmp -s "$boot_override" "$boot_target"; then
      "${SUDO[@]}" install -D -m 0644 "$boot_override" "$boot_target"
      "${SUDO[@]}" systemctl daemon-reload
    fi
    echo "==> Boot service will reuse successful image $QATOOLBOX_IMAGE"
  fi
fi

echo "Public deployment succeeded: http://127.0.0.1:${APP_PORT}/health/"
