#!/bin/bash
# ---------------------------------------------------------------------------
# Self-contained LabBook bundle: the app + its OWN MariaDB in one Podman pod.
#
# Designed to coexist with cPanel/WHM: it publishes ONLY to a loopback port
# ($BIND, default 127.0.0.1:5000) and runs its own database inside the pod, so
# it never touches the host's Apache (80/443) or the cPanel system MySQL.
# Put a reverse proxy (cPanel subdomain) in front of $BIND to expose it.
#
# Usage:
#   ./deploy/labbook-bundle.sh up        # build/seed and start
#   ./deploy/labbook-bundle.sh down      # stop & remove the pod (data volume kept)
#   ./deploy/labbook-bundle.sh status
#   ./deploy/labbook-bundle.sh logs
#
# Env overrides: BIND, APP_IMAGE, DB_IMAGE
# ---------------------------------------------------------------------------
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
POD=labbook-bundle
APP_IMAGE="${APP_IMAGE:-localhost/labbook-python:latest}"
DB_IMAGE="${DB_IMAGE:-docker.io/library/mariadb:11}"
BIND="${BIND:-127.0.0.1:5000}"
DB_VOL=labbook_db_data
STORAGE_VOL=labbook_storage
LOGS_VOL=labbook_logs
RUNTIME="$REPO/deploy/runtime"
SECRET_FILE="$RUNTIME/db_credentials.env"

down() { podman pod rm -f "$POD" 2>/dev/null || true; }

status() {
  podman pod ps --filter name="$POD" || true
  podman ps --filter pod="$POD" --format '{{.Names}}\t{{.Status}}' || true
}

logs() { podman logs --tail 50 "${POD}-app" 2>&1 || true; }

up() {
  command -v podman >/dev/null || { echo "ERROR: podman not installed"; exit 1; }
  podman image exists "$APP_IMAGE" || { echo "ERROR: $APP_IMAGE not found. Build (make devbuild) or load the saved tarball first."; exit 1; }
  mkdir -p "$RUNTIME"

  # 1) Credentials: reuse if present so the app stays in sync with the existing DB volume.
  if [ -f "$SECRET_FILE" ]; then
    # shellcheck disable=SC1090
    . "$SECRET_FILE"
  else
    DB_PASS="$(openssl rand -hex 16)"; DB_ROOT_PASS="$(openssl rand -hex 16)"
    ( umask 077; printf 'DB_PASS=%s\nDB_ROOT_PASS=%s\n' "$DB_PASS" "$DB_ROOT_PASS" > "$SECRET_FILE" )
    echo "Generated DB credentials -> $SECRET_FILE (keep this safe)"
  fi

  # 2) Runtime default_settings.py — the BE makes an import-time DB call using these
  #    BEFORE env overrides, so point them at the bundled DB on the pod's localhost.
  sed -e "s/^DB_USER .*/DB_USER = 'labbook'/" \
      -e "s/^DB_PWD .*/DB_PWD  = '${DB_PASS}'/" \
      -e "s/^DB_HOST .*/DB_HOST = '127.0.0.1'/" \
      "$REPO/labbook_BE/default_settings.py" > "$RUNTIME/default_settings.py"

  down
  # 3) Pod published ONLY on the loopback bind (coexists with cPanel Apache).
  podman pod create --name="$POD" --publish="${BIND}:80"

  # 4) Bundled MariaDB (pod-internal 127.0.0.1:3306). Auto-seeds SIGL from the demo dump on first init.
  podman run -d --pod="$POD" --name="${POD}-db" \
    -e MARIADB_ROOT_PASSWORD="$DB_ROOT_PASS" \
    -e MARIADB_DATABASE=SIGL \
    -e MARIADB_USER=labbook \
    -e MARIADB_PASSWORD="$DB_PASS" \
    -v "${DB_VOL}:/var/lib/mysql:Z" \
    -v "$REPO/etc/sql/demo_dump.sql:/docker-entrypoint-initdb.d/10-demo.sql:ro,Z" \
    "$DB_IMAGE" --sql-mode='' --character-set-server=utf8 --collation-server=utf8_unicode_ci

  # 5) Wait until the DB is up AND the demo data is loaded.
  echo -n "Waiting for MariaDB + SIGL data"
  for i in $(seq 1 80); do
    if podman exec "${POD}-db" mariadb -ulabbook -p"$DB_PASS" \
         -e "select 1 from SIGL.sigl_user_data limit 1" >/dev/null 2>&1; then
      echo " ready"; break
    fi
    echo -n "."; sleep 3
    if [ "$i" = 80 ]; then echo " TIMEOUT"; podman logs --tail 40 "${POD}-db"; exit 1; fi
  done

  # 6) App container: baked image, only default_settings overridden; storage/logs persisted in volumes.
  podman run -d --pod="$POD" --name="${POD}-app" \
    --tz=local -e LANG=C.UTF-8 \
    -e GUNICORN_CMD_ARGS=--workers=5 \
    -e LABBOOK_DB_USER=labbook -e LABBOOK_DB_PWD="$DB_PASS" -e LABBOOK_DB_NAME=SIGL \
    -e LABBOOK_DB_HOST=127.0.0.1 -e LABBOOK_DEBUG=0 -e LABBOOK_POD_NAME="$POD" \
    -v "$RUNTIME/default_settings.py:/home/apps/labbook_BE/labbook_BE/default_settings.py:ro,Z" \
    -v "${STORAGE_VOL}:/storage:Z" \
    -v "${LOGS_VOL}:/home/apps/logs:Z" \
    "$APP_IMAGE"

  echo "Pod '$POD' is up. LabBook will be at http://${BIND}/sigl in ~60s (DB migrate + boot)."
}

case "${1:-up}" in
  up) up ;;
  down) down; echo "stopped (data volume '$DB_VOL' kept)" ;;
  status) status ;;
  logs) logs ;;
  *) echo "usage: $0 up|down|status|logs"; exit 2 ;;
esac
