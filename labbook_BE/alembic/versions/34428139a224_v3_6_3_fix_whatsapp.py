"""v3_6_3_fix_whatsapp

Revision ID: 34428139a224
Revises: da0ded1dd31a
Create Date: 2025-10-23 08:42:23.660932

"""
from alembic import op
from sqlalchemy import text

from datetime import datetime


# revision identifiers, used by Alembic.
revision = '34428139a224'
down_revision = 'da0ded1dd31a'
branch_labels = None
depends_on = None


def upgrade():
    print("--- " + str(datetime.today()) + "---")
    print("START of migration v3_6_3_fix_whatsapp revision=34428139a224")

    # Get the current
    conn = op.get_bind()

    # Add column eqp_status
    try:
        conn.execute(text("ALTER TABLE sending_model ADD COLUMN mdl_lang varchar(10) not null DEFAULT 'en'"))
    except Exception as err:
        print("ERROR add column mdl_lang to sending_model,\n\terr=" + str(err))

    print(str(datetime.today()) + " : END of migration v3_6_3_fix_whatsapp revision=34428139a224")


def downgrade():
    """
    No-op by design.

    This migration is intentionally irreversible per the organization's
    forward-only policy. It includes destructive operations and/or renames
    that cannot be safely undone. To roll back, restore a verified backup
    taken before revision 34428139a224.
    """
    print("downgrade skipped: irreversible migration 34428139a224 (forward-only policy)")
