"""v3_6_18_increase_size_of_columns

Revision ID: ef1f9f565b91
Revises: 43eed8e3b5c6
Create Date: 2026-03-31 10:15:40.014910

"""
from alembic import op
from sqlalchemy import text
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'ef1f9f565b91'
down_revision = '43eed8e3b5c6'
branch_labels = None
depends_on = None


def upgrade():
    print("--- " + str(datetime.today()) + "---")
    print("START of migration v3_6_18_increase_size_of_columns revision=ef1f9f565b91")

    conn = op.get_bind()

    # MODIFY column tpl_file in template_setting
    try:
        conn.execute(text("ALTER TABLE template_setting MODIFY tpl_file VARCHAR(255) NOT NULL"))
    except Exception as err:
        print("ERROR modify column tpl_file in template_setting,\n\terr=" + str(err))

    # MODIFY column file in sigl_11_data
    try:
        conn.execute(text("ALTER TABLE sigl_11_data MODIFY file VARCHAR(255) NOT NULL"))
    except Exception as err:
        print("ERROR modify column file in sigl_11_data,\n\terr=" + str(err))

    # MODIFY column file in sigl_11_data_deleted
    try:
        conn.execute(text("ALTER TABLE sigl_11_data_deleted MODIFY file VARCHAR(255) NOT NULL"))
    except Exception as err:
        print("ERROR modify column file in sigl_11_data_deleted,\n\terr=" + str(err))

    try:
        conn.execute(text("""
            INSERT INTO sigl_06_data (id_owner, identifiant, label, value)
            SELECT 1, 'audit_trail_enabled', 'Audit trail activé', '1'
            WHERE NOT EXISTS (
                SELECT 1 FROM sigl_06_data WHERE identifiant = 'audit_trail_enabled'
            )
        """))
    except Exception as err:
        print("ERROR insert audit_trail_enabled in sigl_06_data,\n\terr=" + str(err))

    print(str(datetime.today()) + " : END of migration v3_6_18_increase_size_of_columns revision=ef1f9f565b91")


def downgrade():
    """
    No-op by design.

    This migration is intentionally irreversible per the organization's
    forward-only policy. It includes destructive operations and/or renames
    that cannot be safely undone. To roll back, restore a verified backup
    taken before revision ef1f9f565b91.
    """
    print("downgrade skipped: irreversible migration ef1f9f565b91 (forward-only policy)")
