"""v3_6_7_audit_trail

Revision ID: 423f282380a8
Revises: 85720bfb7d7e
Create Date: 2025-12-03 16:06:08.498830

"""
from alembic import op
from sqlalchemy import text
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '423f282380a8'
down_revision = '85720bfb7d7e'
branch_labels = None
depends_on = None


def upgrade():
    print("--- " + str(datetime.today()) + "---")
    print("START of migration v3_6_7_audit_trail revision=423f282380a8")

    conn = op.get_bind()

    # Insert profile rights
    try:
        conn.execute(text('''
                          insert into profile_rights (prr_ser, prr_date, prr_by_user, prr_rank, prr_type, prr_label, prr_tag)
                          values
                          (183, NOW(), 0, 30,"ADMIN","Consulter le journal d'audit", "ADMIN_183")
                          '''))
    except Exception as err:
        print("ERROR insert new default profile_rights,\n\terr=" + str(err))

    # Insert default permissions to Y for Admin
    try:
        conn.execute(text('''
                          INSERT INTO profile_permissions (prp_date, prp_by_user, prp_pro, prp_prr, prp_granted)
                          SELECT NOW(), 0, profiles.prp_pro, prr.prr_ser, 'Y'
                          FROM profile_rights AS prr
                          JOIN ( SELECT 1 AS prp_pro ) AS profiles ON 1=1
                          WHERE prr.prr_ser = 183
                        '''))
    except Exception as err:
        print("ERROR inserting new default profile_permissions to Y for A,\n\terr=" + str(err))

    # Insert default permissions to N for Others
    try:
        conn.execute(text('''
                          INSERT INTO profile_permissions (prp_date, prp_by_user, prp_pro, prp_prr, prp_granted)
                          SELECT NOW(), 0, profiles.prp_pro, prr.prr_ser, 'N'
                          FROM profile_rights AS prr
                          JOIN (
                              SELECT distinct pro_ser AS prp_pro
                              from profile_role
                              where pro_ser not in (1)
                          ) AS profiles
                          ON 1=1
                          WHERE prr.prr_ser = 183
                        '''))
    except Exception as err:
        print("ERROR inserting new default profile_permissions to N for others,\n\terr=" + str(err))

    # Create audit_trail table
    try:
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS audit_trail (
                aud_ser BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
                aud_date_utc DATETIME NOT NULL,
                aud_user_login VARCHAR(64) NULL,
                aud_user_display VARCHAR(128) NULL,
                aud_user_role VARCHAR(64) NULL,
                aud_action VARCHAR(128) NOT NULL,
                aud_resource_type VARCHAR(64) NULL,
                aud_resource_id VARCHAR(64) NULL,
                aud_status VARCHAR(32) NULL,
                aud_event_type VARCHAR(1) NOT NULL DEFAULT "E",
                aud_client_ip VARCHAR(45) NULL,
                aud_details JSON NULL,
                PRIMARY KEY (aud_ser),
                KEY idx_audit_date (aud_date_utc),
                KEY idx_audit_action (aud_action),
                KEY idx_audit_resource (aud_resource_type, aud_resource_id),
                KEY idx_audit_status (aud_status),
                KEY idx_aud_event_type (aud_event_type)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        '''))
    except Exception as err:
        print("ERROR creating audit_trail table, err=" + str(err))

    print(str(datetime.today()) + " : END of migration v3_6_7_audit_trail revision=423f282380a8")


def downgrade():
    """
    No-op by design.

    This migration is intentionally irreversible per the organization's
    forward-only policy. It includes destructive operations and/or renames
    that cannot be safely undone. To roll back, restore a verified backup
    taken before revision 423f282380a8.
    """
    print("downgrade skipped: irreversible migration 423f282380a8 (forward-only policy)")
