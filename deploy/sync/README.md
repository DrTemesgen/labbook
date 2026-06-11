# LabBook multi-site daily sync (local-first, one-way to HQ)

For deployments where each lab runs its **own** LabBook instance (local server +
tablets on local Wi-Fi, works without internet) and ships its data to a central
HQ on a schedule for **backup and reporting**.

## Design rule
> Every record has **one owner** and flows **one direction**.

- Each lab is the sole owner of its patients/results — entered/edited only there.
- Daily, the lab pushes an encrypted dump **up** to HQ.
- HQ loads it into an **isolated per-site database** `labbook_site_<id>` and
  treats it as **read-only** (backup + cross-lab reporting). HQ never edits it.
- Isolated DBs ⇒ two labs both having "patient #1" never collide.

**Not** bidirectional. If HQ ever needs to edit lab data, that's multi-master
replication with conflict resolution — a separate, much larger design.

## Why this fits the field model
- Encrypted daily dump is **tiny** (~190 KB on the demo DB) — the link only needs
  to be up briefly, so intermittent/Starlink connectivity is fine.
- Local-first means the lab keeps working during an outage; only the sync waits.
- The big power draw in the field is the **Starlink dish (~50–75 W)**, not the
  tablet (~5–15 W) or a Pi-class local server (~10–25 W) — size solar for the dish.

## Files
- `labbook-sync-push.sh` — lab box, daily cron. dump → gzip → AES-256 → upload.
- `labbook-sync-ingest.sh` — HQ, hourly cron. checksum → decrypt → per-site DB.

## One-time setup
1. **Shared key** (AES-256), generated once on HQ, copied to every box out-of-band:
   ```
   openssl rand -base64 32 > /etc/labbook-sync.key && chmod 400 /etc/labbook-sync.key
   ```
2. **Transport**: SSH key from each box to a restricted HQ user whose inbox is
   `/srv/labbook-sync/inbox`. (Or swap rsync for `rclone` to object storage.)
3. **Per-box config** `/etc/labbook-sync.conf`:
   ```
   SITE_ID=lab01
   DEST_SSH=hqsync@hq.aslmacademy.org
   ```
4. **Cron**:
   - box: `30 2 * * *  /opt/labbook/deploy/sync/labbook-sync-push.sh`
   - HQ:  `17 * * * *  /opt/labbook/deploy/sync/labbook-sync-ingest.sh`

## Safety properties (verified in sandbox)
- **Encrypted at rest and in transit** (AES-256; wrong key cannot decrypt).
- **Integrity-checked** (SHA-256 per file; mismatch is skipped, not loaded).
- **Idempotent / full-refresh** — re-running just reloads the latest snapshot.
- **Least privilege** — the `labbook` app user cannot create databases; only the
  HQ ingest uses root, and only to build the isolated per-site DBs.
- **Retention** — boxes keep the newest N local dumps; HQ archives processed ones.

## View / report on a lab's data at HQ
Each `labbook_site_<id>` is a complete SIGL schema, so you can either point a
**read-only** LabBook front-end at it to browse, or query it directly. For
cross-lab dashboards, roll selected tables into one reporting DB tagged by `site`.
