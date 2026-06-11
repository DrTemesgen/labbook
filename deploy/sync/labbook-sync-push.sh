#!/bin/bash
# =============================================================================
# labbook-sync-push.sh  —  runs on each LAB box (daily via cron)
# =============================================================================
# Dumps the local LabBook database, compresses, encrypts (AES-256), and uploads
# it to HQ. ONE-WAY: this box is the sole owner of its data; nothing is pulled
# back. Verified end-to-end in the WSL sandbox (lab -> HQ, 119 tables/11 users
# restored intact, ~190 KB encrypted dump).
#
# Setup (once):
#   1. Generate the shared key on HQ and copy to every box (out-of-band, 0400):
#        openssl rand -base64 32 > /etc/labbook-sync.key && chmod 400 /etc/labbook-sync.key
#   2. Create an SSH key on the box, add its public key to HQ's sync user.
#   3. Put per-box settings in /etc/labbook-sync.conf (at least SITE_ID, DEST_SSH).
#   4. Cron (daily 02:30):  30 2 * * * /opt/labbook/deploy/sync/labbook-sync-push.sh
# =============================================================================
set -euo pipefail

[ -f /etc/labbook-sync.conf ] && . /etc/labbook-sync.conf
SITE_ID="${SITE_ID:?set SITE_ID (e.g. lab01) in /etc/labbook-sync.conf}"
DB_CONTAINER="${DB_CONTAINER:-labbook-bundle-db}"
DB_NAME="${DB_NAME:-SIGL}"
CRED_ENV="${CRED_ENV:-/opt/labbook/deploy/runtime/db_credentials.env}"
KEYFILE="${KEYFILE:-/etc/labbook-sync.key}"          # shared AES secret (0400)
OUTDIR="${OUTDIR:-/var/backups/labbook-sync}"
KEEP="${KEEP:-14}"                                   # local copies to retain
DEST_SSH="${DEST_SSH:-}"                             # e.g. hqsync@hq.aslmacademy.org
DEST_PATH="${DEST_PATH:-/srv/labbook-sync/inbox}"
LOG="${LOG:-/var/log/labbook-sync-push.log}"

log(){ echo "$(date '+%F %T') [$SITE_ID] $*" | tee -a "$LOG" ; }

. "$CRED_ENV"                                         # provides DB_ROOT_PASS
mkdir -p "$OUTDIR"
base="labbook_${SITE_ID}_$(date +%F_%H%M%S)"
enc="$OUTDIR/$base.sql.gz.enc"

log "dump + gzip + AES-256 -> $base.sql.gz.enc"
podman exec "$DB_CONTAINER" mariadb-dump -uroot -p"$DB_ROOT_PASS" \
    --single-transaction --routines --triggers --events "$DB_NAME" \
  | gzip -c \
  | openssl enc -aes-256-cbc -pbkdf2 -salt -pass file:"$KEYFILE" \
  > "$enc"
sha256sum "$enc" | awk '{print $1}' > "$enc.sha256"
log "size $(du -h "$enc" | cut -f1)"

# ---- upload: rsync over SSH (default). See alternatives below. ----
if [ -n "$DEST_SSH" ]; then
  log "upload -> $DEST_SSH:$DEST_PATH"
  rsync -az --partial "$enc" "$enc.sha256" "$DEST_SSH:$DEST_PATH/"
  log "upload done"
else
  log "DEST_SSH unset — dump kept locally only ($enc)"
fi
# Alternatives instead of rsync:
#   scp "$enc" "$enc.sha256" "$DEST_SSH:$DEST_PATH/"
#   rclone copy "$enc" remote:labbook-sync/inbox/      # S3 / Backblaze B2 / GDrive

# ---- local retention (keep newest $KEEP) ----
ls -1t "$OUTDIR"/labbook_${SITE_ID}_*.sql.gz.enc 2>/dev/null | tail -n +$((KEEP+1)) | while read -r old; do
  rm -f "$old" "$old.sha256" ; log "pruned $old"
done
log "OK"
