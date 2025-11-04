#!/bin/bash
set -euo pipefail

APP_HOME="/home/apps/labbook_BE/labbook_BE"
PY="$APP_HOME/venv/bin/python"

export LOCAL_SETTINGS="$APP_HOME/local_settings.py"
export PYTHONPATH="$APP_HOME"

cd "$APP_HOME"
exec "$PY" -m app.automation.runner
