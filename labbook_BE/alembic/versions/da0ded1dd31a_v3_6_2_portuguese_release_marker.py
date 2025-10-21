"""v3_6_2_portuguese_release_marker

Revision ID: da0ded1dd31a
Revises: ed09fb3dd670
Create Date: 2025-10-20 15:51:01.782243

"""
from alembic import op
from sqlalchemy import text

from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'da0ded1dd31a'
down_revision = 'ed09fb3dd670'
branch_labels = None
depends_on = None


def upgrade():
    print("START migration v3_6_2_portuguese_release_marker revision=da0ded1dd31a")

    conn = op.get_bind()

    # ask for update translation in DB
    try:
        # insert a line in init_version
        conn.execute(text("insert into init_version (ini_date, ini_stat) values (NOW(), 'Y')"))
    except Exception as err:
        print("ERROR insert init_version,\n\terr=" + str(err))

    print(str(datetime.today()) + " : END of migration v3_6_2_portuguese_release_marker revision=da0ded1dd31a")


def downgrade():
    """
    No-op by design.

    This migration is intentionally irreversible per the organization's
    forward-only policy. It includes destructive operations and/or renames
    that cannot be safely undone. To roll back, restore a verified backup
    taken before revision da0ded1dd31a.
    """
    print("downgrade skipped: irreversible migration da0ded1dd31a (forward-only policy)")
