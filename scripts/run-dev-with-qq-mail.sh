#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
KEYCHAIN_SERVICE="modeshift-qq-smtp"
MAIL_ACCOUNT="${MODESHIFT_QQ_MAIL_ACCOUNT:-1009383129@qq.com}"

if ! command -v security >/dev/null 2>&1; then
  echo "macOS 钥匙串命令不可用" >&2
  exit 1
fi

EMAIL_HOST_PASSWORD="$(security find-generic-password -s "$KEYCHAIN_SERVICE" -a "$MAIL_ACCOUNT" -w)"
export EMAIL_HOST_PASSWORD
export EMAIL_HOST="smtp.qq.com"
export EMAIL_PORT="587"
export EMAIL_USE_TLS="true"
export EMAIL_HOST_USER="$MAIL_ACCOUNT"
export DEFAULT_FROM_EMAIL="$MAIL_ACCOUNT"
export DJANGO_SETTINGS_MODULE="config.settings.development"

cd "$PROJECT_DIR"
if python3 -c 'import daphne' >/dev/null 2>&1; then
  exec python3 -m daphne -b 127.0.0.1 -p 8000 asgi:application
fi
exec python3 manage.py runserver 127.0.0.1:8000 --noreload
