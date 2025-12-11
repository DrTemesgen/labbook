#!/bin/bash
set -euo pipefail

# Infinite loop to run logrotate once a day
while true; do
    # Run logrotate for LabBook logs
    logrotate -s /storage/log/logrotate.status /etc/logrotate.d/labbook || echo "logrotate failed" >&2

    # Sleep 24 hours before next rotation
    sleep 86400
done
