"""v3_6_19_before_new_ubuntu

Revision ID: 2c884d401740
Revises: ef1f9f565b91
Create Date: 2026-04-29 14:46:52.022006

"""
from alembic import op
from sqlalchemy import text
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '2c884d401740'
down_revision = 'ef1f9f565b91'
branch_labels = None
depends_on = None


def upgrade():
    print("--- " + str(datetime.today()) + "---")
    print("START of migration v3_6_19_before_new_ubuntu revision=2c884d401740")

    conn = op.get_bind()

    # Add pat_amicare column (AmiCare patient ID)
    try:
        conn.execute(text("""
            ALTER TABLE sigl_03_data
            ADD COLUMN pat_amicare INT UNSIGNED NOT NULL DEFAULT 0
        """))
    except Exception as err:
        print("ERROR add column pat_amicare in sigl_03_data,\n\terr=" + str(err))

    print(str(datetime.today()) + " : END of migration v3_6_19_before_new_ubuntu revision=2c884d401740")


def downgrade():
    """
    No-op by design.

    This migration is intentionally irreversible per the organization's
    forward-only policy. It includes destructive operations and/or renames
    that cannot be safely undone. To roll back, restore a verified backup
    taken before revision 2c884d401740.
    """
    print("downgrade skipped: irreversible migration 2c884d401740 (forward-only policy)")
