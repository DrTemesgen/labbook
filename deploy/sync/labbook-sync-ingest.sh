#!/bin/bash
# =============================================================================
# labbook-sync-ingest.sh  —  runs on HQ (cron, e.g. hourly or a few times/day)
# =============================================================================
# Loads each lab's encrypted dump into an ISOLATED per-site database
# (labbook_site_<id>) so sites never collide. The central copy is READ-ONLY
# (backup + reporting); HQ does not edit lab data. Full-refresh each run
# (latest snapshot replaces the previous) — simplest and conflict-free.
#
# Setup (once):
#   - Same /etc/labbook-sync.key as the boxes (out-of-band, 0400).
#   - A restricted SSH user (e.g. hqsync) whose home receives uploads into INBOX.
#   - Cron (hourly):  17 * * * * /opt/labbook/deploy/sync/labbook-sync-ingest.sh
#
# View a lab's data: point a READ-ONLY LabBook FE at any labbook_site_<id> DB,
# or query it directly for cross-lab reports (tag rows by site on the way in).
# =============================================================================
set -euo pipefail

[ -f /etc/labbook-sync-hq.conf ] && . /etc/labbook-sync-hq.conf
INBOX="${INBOX:-/srv/labbook-sync/inbox}"
ARCHIVE="${ARCHIVE:-/srv/labbook-sync/archive}"
KEYFILE="${KEYFILE:-/etc/labbook-sync.key}"
DB_CONTAINER="${DB_CONTAINER:-labbook-bundle-db}"
CRED_ENV="${CRED_ENV:-/opt/labbook/deploy/runtime/db_credentials.env}"
PREFIX="${PREFIX:-labbook_site_}"
LOG="${LOG:-/var/log/labbook-sync-ingest.log}"

log(){ echo "$(date '+%F %T') [HQ] $*" | tee -a "$LOG" ; }

. "$CRED_ENV"                                         # provides DB_ROOT_PASS
mkdir -p "$ARCHIVE"
shopt -s nullglob

for enc in "$INBOX"/*.sql.gz.enc; do
  base="$(basename "$enc" .sql.gz.enc)"

  # integrity: verify checksum if present
  if [ -f "$INBOX/$base.sha256" ]; then
    want="$(cat "$INBOX/$base.sha256")"
    got="$(sha256sum "$enc" | awk '{print $1}')"
    if [ "$want" != "$got" ]; then log "CHECKSUM FAIL $base — skipping"; continue; fi
  fi

  site="$(echo "$base" | sed -E 's/^labbook_([^_]+)_.*/\1/')"
  target="${PREFIX}${site}"
  log "ingest $base -> $target (full refresh)"

  podman exec -i "$DB_CONTAINER" mariadb -uroot -p"$DB_ROOT_PASS" \
    -e "DROP DATABASE IF EXISTS \`$target\`; CREATE DATABASE \`$target\` CHARACTER SET utf8mb4;"

  if openssl enc -d -aes-256-cbc -pbkdf2 -pass file:"$KEYFILE" -in "$enc" \
       | gunzip -c \
       | podman exec -i "$DB_CONTAINER" mariadb -uroot -p"$DB_ROOT_PASS" "$target"; then
    mv "$enc" "$ARCHIVE/"
    [ -f "$INBOX/$base.sha256" ] && mv "$INBOX/$base.sha256" "$ARCHIVE/"
    log "OK $site"
  else
    log "LOAD FAILED $base — left in inbox for retry"
  fi
done
log "done"
