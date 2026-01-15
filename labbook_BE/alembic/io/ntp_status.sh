#!/bin/bash

if [ -d "/storage/io" ]; then
    BASE="/storage/io"
elif [ -d "/home/labbook_src/devrun_storage/io" ]; then
    BASE="/home/labbook_src/devrun_storage/io"
else
    exit 1
fi

OUT="$BASE/ntp_status.out"
TMP="${OUT}.tmp"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

SYNC="0"
RAW=""
ERR=""

if command -v timedatectl >/dev/null 2>&1; then
    RAW="$(timedatectl show -p NTPSynchronized --value 2>/dev/null)"
    [ "$RAW" = "yes" ] && SYNC="1"
else
    ERR="timedatectl_not_found"
fi

if [ -n "$ERR" ]; then
    echo "ts_utc=$TS synced=0 error=$ERR" > "$TMP"
else
    echo "ts_utc=$TS synced=$SYNC raw=NTPSynchronized=$RAW" > "$TMP"
fi

mv -f "$TMP" "$OUT"
