"""v3_6_8_result_mapping

Revision ID: 7dcf36bd5c39
Revises: 423f282380a8
Create Date: 2025-12-22 09:07:18.506883

"""
from alembic import op
from sqlalchemy import text
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '7dcf36bd5c39'
down_revision = '423f282380a8'
branch_labels = None
depends_on = None


def upgrade():
    print("--- " + str(datetime.today()) + "---")
    print("START of migration v3_6_8_result_mapping revision=7dcf36bd5c39")

    conn = op.get_bind()

    # Add mapped LabBook result code (keep anr_code as raw analyzer code)
    try:
        conn.execute(text('''
                          ALTER TABLE analyzer_result
                          ADD COLUMN anr_lb_code VARCHAR(10) NULL AFTER anr_code
                          '''))
    except Exception as err:
        print("ERROR alter analyzer_result add anr_lb_code, err=" + str(err))

    print(str(datetime.today()) + " : END of migration v3_6_8_result_mapping revision=7dcf36bd5c39")


def downgrade():
    """
    No-op by design.

    This migration is intentionally irreversible per the organization's
    forward-only policy. It includes destructive operations and/or renames
    that cannot be safely undone. To roll back, restore a verified backup
    taken before revision 7dcf36bd5c39.
    """
    print("downgrade skipped: irreversible migration 7dcf36bd5c39 (forward-only policy)")
