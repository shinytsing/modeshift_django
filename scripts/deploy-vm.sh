#!/usr/bin/env bash
# Deploy QAToolBox to a single Ubuntu VMware guest. Safe to run again for updates.
set -Eeuo pipefail

REPOSITORY_URL="${1:-https://github.com/shinytsing/modeshift_django.git}"
PROJECT_DIR="${QATOOLBOX_DIR:-$HOME/modeshift_django}"
APP_PORT="${APP_PORT:-8000}"

if ! command -v apt-get >/dev/null; then
  echo "This script supports an Ubuntu/Debian VMware guest only." >&2
  exit 1
fi

SUDO=()
if [[ $EUID -ne 0 ]]; then
  SUDO=(sudo)
fi

install_docker() {
  if command -v docker >/dev/null && docker compose version >/dev/null 2>&1; then
    return
  fi

  echo "==> Installing Docker Engine and Docker Compose"
  "${SUDO[@]}" apt-get update
  "${SUDO[@]}" apt-get install -y ca-certificates curl git
  curl -fsSL https://get.docker.com | "${SUDO[@]}" sh
  "${SUDO[@]}" systemctl enable --now docker
  "${SUDO[@]}" usermod -aG docker "${SUDO_USER:-$USER}" || true
}

sync_project() {
  if [[ -d "$PROJECT_DIR/.git" ]]; then
    echo "==> Updating $PROJECT_DIR"
    git -C "$PROJECT_DIR" pull --ff-only
  elif [[ -e "$PROJECT_DIR" ]]; then
    echo "$PROJECT_DIR exists but is not a Git checkout; choose another QATOOLBOX_DIR." >&2
    exit 1
  else
    echo "==> Cloning project"
    git clone --depth 1 "$REPOSITORY_URL" "$PROJECT_DIR"
  fi
}

write_environment() {
  local vm_ip
  vm_ip="$(hostname -I | awk '{print $1}')"
  if [[ -z "$vm_ip" ]]; then
    vm_ip="localhost"
  fi

  if [[ ! -f "$PROJECT_DIR/.env.vm" ]]; then
    echo "==> Creating local VM secrets in $PROJECT_DIR/.env.vm"
    umask 077
    {
      printf 'POSTGRES_PASSWORD=%s\n' "$(openssl rand -hex 24)"
      printf 'REDIS_PASSWORD=%s\n' "$(openssl rand -hex 24)"
      printf 'DJANGO_SECRET_KEY=%s\n' "$(openssl rand -hex 48)"
      printf 'ALLOWED_HOSTS=localhost,127.0.0.1,%s\n' "$vm_ip"
      printf 'APP_PORT=%s\n' "$APP_PORT"
    } > "$PROJECT_DIR/.env.vm"
  fi
}

main() {
  install_docker
  sync_project
  write_environment

  local docker_command=(docker)
  if ! docker info >/dev/null 2>&1; then
    docker_command=("${SUDO[@]}" docker)
  fi
  compose() {
    "${docker_command[@]}" compose --env-file "$PROJECT_DIR/.env.vm" \
      -f "$PROJECT_DIR/docker/docker-compose.vm.yml" "$@"
  }

  echo "==> Building and starting QAToolBox"
  compose up -d --build --remove-orphans

  local vm_ip attempt
  vm_ip="$(hostname -I | awk '{print $1}')"
  for attempt in {1..30}; do
    if curl -fsS "http://127.0.0.1:${APP_PORT}/health/" >/dev/null; then
      echo
      echo "Deployment succeeded. Open: http://${vm_ip}:${APP_PORT}"
      echo "Logs: cd $PROJECT_DIR && ${docker_command[*]} compose --env-file .env.vm -f docker/docker-compose.vm.yml logs -f web"
      exit 0
    fi
    sleep 2
  done

  echo "Deployment did not become healthy. Recent web logs:" >&2
  compose logs --tail=100 web >&2
  exit 1
}

main "$@"
