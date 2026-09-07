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
  if [[ "${QATOOLBOX_SKIP_GIT_SYNC:-false}" == "true" ]]; then
    # GitHub Actions already supplied this minimal deployment bundle as an
    # artifact. Avoid a second GitHub fetch on the VMware runner, whose
    # network path can be less reliable than the Actions artifact service.
    local script_dir source_compose
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    source_compose="$script_dir/../docker/docker-compose.vm.yml"
    if [[ ! -f "$source_compose" ]]; then
      echo "Deployment bundle is missing docker/docker-compose.vm.yml." >&2
      exit 1
    fi

    echo "==> Updating deployment configuration in $PROJECT_DIR"
    mkdir -p "$PROJECT_DIR/docker"
    install -m 0644 "$source_compose" "$PROJECT_DIR/docker/docker-compose.vm.yml"
    return
  fi

  if [[ -d "$PROJECT_DIR/.git" ]]; then
    if git -C "$PROJECT_DIR" diff --quiet && git -C "$PROJECT_DIR" diff --cached --quiet; then
      echo "==> Updating $PROJECT_DIR"
      git -C "$PROJECT_DIR" pull --ff-only
    else
      # A VM often contains an older experimental checkout. Never overwrite it:
      # deploy the current repository to a sibling directory instead.
      PROJECT_DIR="${PROJECT_DIR}-deploy"
      if [[ -d "$PROJECT_DIR/.git" ]]; then
        echo "==> Updating separate deployment checkout $PROJECT_DIR"
        git -C "$PROJECT_DIR" pull --ff-only
      elif [[ -e "$PROJECT_DIR" ]]; then
        echo "$PROJECT_DIR exists but is not a Git checkout; set QATOOLBOX_DIR to a clean directory." >&2
        exit 1
      else
        echo "==> Existing checkout has local changes; cloning a safe deployment copy"
        git clone --depth 1 "$REPOSITORY_URL" "$PROJECT_DIR"
      fi
    fi
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

  if [[ -z "${QATOOLBOX_IMAGE:-}" ]]; then
    echo "QATOOLBOX_IMAGE is required; deploy through the GitHub Actions image-build workflow." >&2
    exit 1
  fi
  if [[ -z "${GHCR_USERNAME:-}" || -z "${GHCR_PULL_TOKEN:-}" ]]; then
    echo "GHCR_USERNAME and GHCR_PULL_TOKEN are required to pull the private production image." >&2
    exit 1
  fi

  echo "==> Logging in to GitHub Container Registry"
  printf '%s' "$GHCR_PULL_TOKEN" | "${docker_command[@]}" login ghcr.io \
    --username "$GHCR_USERNAME" --password-stdin

  echo "==> Pulling and starting prebuilt QAToolBox image $QATOOLBOX_IMAGE"
  export QATOOLBOX_IMAGE
  compose pull web

  # A persistent PostgreSQL volume keeps the password used when it was first
  # initialized. If .env.vm is later recreated, POSTGRES_PASSWORD alone does
  # not update that existing role and the web container enters a restart loop.
  # Start infrastructure first, then align the database role over its trusted
  # local socket before starting Django. This preserves all existing data.
  local postgres_password db_ready
  postgres_password="$(sed -n 's/^POSTGRES_PASSWORD=//p' "$PROJECT_DIR/.env.vm" | head -n 1)"
  if [[ -z "$postgres_password" ]]; then
    echo "POSTGRES_PASSWORD is missing from $PROJECT_DIR/.env.vm" >&2
    exit 1
  fi

  echo "==> Starting PostgreSQL and Redis"
  compose up -d --no-build db redis
  db_ready=false
  for attempt in {1..15}; do
    if compose exec -T db pg_isready -U qatoolbox -d qatoolbox_vm >/dev/null 2>&1; then
      db_ready=true
      break
    fi
    sleep 2
  done
  if [[ "$db_ready" != "true" ]]; then
    echo "PostgreSQL did not become ready." >&2
    compose logs --tail=50 db >&2
    exit 1
  fi

  echo "==> Aligning the persistent PostgreSQL role password"
  printf '%s\n' \
    '\\getenv deployment_password QATOOLBOX_DEPLOYMENT_DB_PASSWORD' \
    "ALTER ROLE qatoolbox WITH PASSWORD :'deployment_password';" | \
    compose exec -T -u postgres -e "QATOOLBOX_DEPLOYMENT_DB_PASSWORD=$postgres_password" \
      db psql -U qatoolbox -d qatoolbox_vm --set=ON_ERROR_STOP=1 >/dev/null

  echo "==> Starting QAToolBox web application"
  compose up -d --no-build --remove-orphans web

  local vm_ip attempt
  vm_ip="$(hostname -I | awk '{print $1}')"
  for attempt in {1..20}; do
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
