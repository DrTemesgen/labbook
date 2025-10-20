"""v3_5_18_portuguese_release_marker

Revision ID: 1a2b3c4d5e6f
Revises: 469be6b8a29b
Create Date: 2025-10-20 10:32:00.000000

"""
from alembic import op
from sqlalchemy import text
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = '469be6b8a29b'
branch_labels = None
depends_on = None


def upgrade():
    print("--- " + str(datetime.today()) + " ---")
    print("START migration v3_5_18_portuguese_release_marker revision=1a2b3c4d5e6f")

    conn = op.get_bind()

    # ask for update translation in DB
    try:
        # insert a line in init_version
        conn.execute(text("insert into init_version (ini_date, ini_stat) values (NOW(), 'Y')"))
    except Exception as err:
        print("ERROR insert init_version,\n\terr=" + str(err))

    print(str(datetime.today()) + " : END of migration v3_5_18_portuguese_release_marker revision=1a2b3c4d5e6f")


def downgrade():
    """
    No-op by design.

    This migration is intentionally irreversible per the organization's
    forward-only policy. It includes destructive operations and/or renames
    that cannot be safely undone. To roll back, restore a verified backup
    taken before revision 1a2b3c4d5e6f.
    """
    print("downgrade skipped: irreversible migration 1a2b3c4d5e6f (forward-only policy)")
