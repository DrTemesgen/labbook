#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
automation runner
"""

import time
import logging
from datetime import datetime

from app import app as flask_app
from app.models.Automation import Automation

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logger = logging.getLogger("automation_runner")
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

# Fixed polling interval in seconds (no env var as requested).
POLL_SEC = 30


def run_once() -> None:
    """
    One scheduler tick:
    - Fetch all active jobs whose next_run_at <= now.
    - For each job, *decide* and delegate execution to the REST/worker layer.
      (This function intentionally avoids doing network calls or heavy work.)
    """
    # Build a timestamp string compatible with SQL DATETIME comparisons.
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Query only due jobs (active + next_run_at <= now).
    jobs = Automation.get_due_jobs(now_str)
    logger.info("%d due jobs at %s", len(jobs), now_str)

    for job in jobs:
        job_id = job.get("ajb_ser")
        job_type = (job.get("ajb_type") or "").lower()
        job_label = job.get("ajb_label") or ""

        # Log the decision. Real execution must be triggered in REST/worker.
        logger.info("due: ser=%s type=%s label=%s", job_id, job_type, job_label)

        # -------------------------------------------------------------------
        # HAND-OFF POINT (to REST/worker)
        # -------------------------------------------------------------------
        # Here, call your REST endpoint / internal worker to execute the job
        # (DHIS2 / activity / billing). Keep the model DB-only.
        #
        # Example (to implement OUTSIDE the model layer):
        #   execute_job_via_rest(job_id)
        #
        # Notes:
        # - The REST/worker should:
        #     * open a run (status=running),
        #     * perform the job,
        #     * finish the run with status + message,
        #     * update ajb_next_run_at and ajb_last_status.
        # - If you want this runner to also update ajb_next_run_at itself,
        #   you can call Automation.scheduler_process_due(max_jobs=...) instead
        #   of this light loop; that method already manages run rows + next_run_at.
        # -------------------------------------------------------------------


def run_forever(poll_sec: int = POLL_SEC) -> None:
    """
    Infinite loop:
    - Enter the Flask app context for DB access.
    - Run one scheduler tick.
    - Sleep for the configured interval.
    - Catch and log any unexpected exception to keep the loop alive.
    """
    logger.info("automation runner started (poll=%ds)", poll_sec)
    while True:
        try:
            # Ensure DB/Flask context is available for model calls.
            with flask_app.app_context():
                run_once()
        except Exception:
            logger.exception("unexpected error in runner loop")
        time.sleep(poll_sec)


if __name__ == "__main__":
    run_forever()

