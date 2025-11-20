#!/bin/bash
set -euo pipefail

APP_HOME="/home/apps/labbook_BE/labbook_BE"
CONFIG_FILE="/home/apps/labbook_BE/local_settings.py"
PY="$APP_HOME/venv/bin/python"

# === Wait for config with timeout ===
# MAX_WAIT_SEC can be overridden by environment; default 120s.
MAX_WAIT_SEC="${MAX_WAIT_SEC:-120}"
elapsed=0
while [ ! -s "$CONFIG_FILE" ]; do
  if [ "$elapsed" -ge "$MAX_WAIT_SEC" ]; then
    echo "ERROR: config file not found or empty after ${MAX_WAIT_SEC}s: $CONFIG_FILE" >&2
    exit 1
  fi
  sleep 1
  elapsed=$((elapsed+1))
done

unset LOCAL_SETTINGS || true
export LOCAL_SETTINGS="$CONFIG_FILE"
unset PYTHONPATH || true
export PYTHONPATH="$APP_HOME"

export LANG="C.UTF-8"
export LC_ALL="C.UTF-8"

cd "$APP_HOME"
exec "$PY" -m app.automation.runner
