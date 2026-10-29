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

if [[ -n "${WECHAT_MINIPROGRAM_APPID:-}" && -n "${WECHAT_MINIPROGRAM_SECRET:-}" ]]; then
  python3 - "$ENV_FILE" <<'PY'
import os
import pathlib
import sys
import tempfile

path = pathlib.Path(sys.argv[1])
keys = ("WECHAT_MINIPROGRAM_APPID", "WECHAT_MINIPROGRAM_SECRET")
values = {key: os.environ.get(key, "") for key in keys}
for key, value in values.items():
    if any(char in value for char in ("\n", "\r", "\0", "'")):
        raise SystemExit(f"{key} contains a character unsupported by the deployment env file")
lines = [line for line in path.read_text().splitlines() if line.split("=", 1)[0] not in keys]
lines.extend(f"{key}='{value}'" for key, value in values.items())
with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, prefix=".env.wechat.", delete=False) as handle:
    handle.write("\n".join(lines) + "\n")
    temporary = pathlib.Path(handle.name)
temporary.chmod(0o600)
temporary.replace(path)
PY
  echo "==> WeChat mini program credentials supplied to public production environment"
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

STACK_SCRIPT="$PROJECT_DIR/scripts/start-production-stack.sh"
if [[ ! -f "$STACK_SCRIPT" ]]; then
  echo "Shared production startup script missing: $STACK_SCRIPT" >&2
  exit 1
fi
compose() {
  QATOOLBOX_DIR="$PROJECT_DIR" bash "$STACK_SCRIPT" compose "$@"
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

echo "==> Starting the shared production stack"
if ! QATOOLBOX_DIR="$PROJECT_DIR" bash "$STACK_SCRIPT" start; then
  if [[ -n "$previous_image" ]] && "${docker_command[@]}" image inspect "$previous_image" >/dev/null 2>&1; then
    echo "==> Rolling back Web and Worker together to $previous_image" >&2
    QATOOLBOX_DIR="$PROJECT_DIR" QATOOLBOX_IMAGE="$previous_image" bash "$STACK_SCRIPT" start >&2 || true
  fi
  exit 1
fi

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

# Keep a diagnostic release marker; every startup reads the canonical .env below.
release_file="$PROJECT_DIR/.deployed-image.env"
release_tmp="$(mktemp "$PROJECT_DIR/.deployed-image.XXXXXX")"
printf 'QATOOLBOX_IMAGE=%s\n' "$QATOOLBOX_IMAGE" > "$release_tmp"
chmod 600 "$release_tmp"
mv "$release_tmp" "$release_file"

# Publish the release selection only after the application checks have passed.
env_tmp="$(mktemp "$PROJECT_DIR/.env.XXXXXX")"
awk -v image="$QATOOLBOX_IMAGE" '
  /^QATOOLBOX_IMAGE=/ { next }
  { print }
  END { print "QATOOLBOX_IMAGE=" image }
' "$ENV_FILE" > "$env_tmp"
chmod 600 "$env_tmp"
mv "$env_tmp" "$ENV_FILE"

# The VM boot unit must call the same startup script and canonical .env.
if command -v systemctl >/dev/null; then
  for unit in modeshift-project.service modeshift-django.service; do
    if systemctl cat "$unit" >/dev/null 2>&1; then
      boot_exec="$(systemctl show "$unit" --property=ExecStart --value)"
      if [[ "$boot_exec" != *"$STACK_SCRIPT"* ]]; then
        echo "$unit still uses another deployment configuration; migrate its ExecStart to $STACK_SCRIPT start." >&2
        exit 1
      fi
    fi
  done
fi

echo "Public deployment succeeded: http://127.0.0.1:${APP_PORT}/health/"
