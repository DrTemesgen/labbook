"""v3_6_5_fix_tables_test

Revision ID: 8a8f1ca60adc
Revises: 76ef200b0496
Create Date: 2025-11-06 11:33:48.495653

"""
from alembic import op
from sqlalchemy import text

from datetime import datetime


# revision identifiers, used by Alembic.
revision = '8a8f1ca60adc'
down_revision = '76ef200b0496'
branch_labels = None
depends_on = None


def upgrade():
    print("--- " + str(datetime.today()) + "---")
    print("START of migration v3_6_5_fix_tables_test revision=8a8f1ca60adc")

    # Get the current
    conn = op.get_bind()

    # ADD COLUMN for ana_lite in sigl_05_data_test
    try:
        conn.execute(text("alter table sigl_05_data_test add column ana_lite varchar(1) not null default 'N'"))
    except Exception as err:
        print("ERROR add column ana_lite to sigl_05_data_test,\n\terr=" + str(err))

    # ADD COLUMN for var_in_report in sigl_07_data
    try:
        conn.execute(text("ALTER TABLE sigl_07_data_test ADD COLUMN var_in_report varchar(1) not null default 'Y'"))
    except Exception as err:
        print("ERROR add column var_in_report to sigl_07_data_test,\n\terr=" + str(err))

    print(str(datetime.today()) + " : END of migration v3_6_5_fix_tables_test revision=8a8f1ca60adc")


def downgrade():
    """
    No-op by design.

    This migration is intentionally irreversible per the organization's
    forward-only policy. It includes destructive operations and/or renames
    that cannot be safely undone. To roll back, restore a verified backup
    taken before revision 8a8f1ca60adc.
    """
    print("downgrade skipped: irreversible migration 8a8f1ca60adc (forward-only policy)")
