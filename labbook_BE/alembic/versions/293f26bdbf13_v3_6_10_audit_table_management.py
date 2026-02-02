"""v3_6_10_audit_table_management

Revision ID: 293f26bdbf13
Revises: eb7fca49548a
Create Date: 2026-01-19 10:18:34.122664

"""
import os
import json

from alembic import op
from sqlalchemy import text
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '293f26bdbf13'
down_revision = 'eb7fca49548a'
branch_labels = None
depends_on = None


def upgrade():
    print("--- " + str(datetime.today()) + "---")
    print("START of migration v3_6_10_audit_table_management revision=293f26bdbf13")

    # Create audit archive directory
    try:
        os.makedirs('/storage/resource/audit/', exist_ok=True)
    except Exception as err:
        print("ERROR create /storage/resource/audit/ err=" + str(err))

    # COPY alembic resource, erase file only if more recent
    try:
        from distutils.dir_util import copy_tree

        fromDirectory = "alembic/resource"
        toDirectory = "/storage/resource"

        copy_tree(fromDirectory, toDirectory, update=1)
    except Exception as err:
        print("ERROR copy alembic resource,\n\terr=" + str(err))

    conn = op.get_bind()

    # DROP useless low-selectivity indexes
    for idx in ("idx_aud_event_type", "idx_audit_status", "idx_audit_action"):
        try:
            conn.execute(text(f"DROP INDEX {idx} ON audit_trail"))
        except Exception as err:
            print(f"ERROR drop index {idx},\n\terr=" + str(err))

    # ADD composite indexes for audit filtering (date always included)
    try:
        conn.execute(text(
            "CREATE INDEX idx_audit_action_date "
            "ON audit_trail (aud_action, aud_date_utc)"
        ))
    except Exception as err:
        print("ERROR create idx_audit_action_date err=" + str(err))

    try:
        conn.execute(text(
            "CREATE INDEX idx_audit_user_date "
            "ON audit_trail (aud_user_login, aud_date_utc)"
        ))
    except Exception as err:
        print("ERROR create idx_audit_user_date,\n\terr=" + str(err))

    try:
        conn.execute(text(
            "CREATE INDEX idx_audit_event_type_date "
            "ON audit_trail (aud_event_type, aud_date_utc)"
        ))
    except Exception as err:
        print("ERROR create idx_audit_event_type_date,\n\t err=" + str(err))

    # ADD audit purge retention (months)
    try:
        conn.execute(
            text(
                "INSERT INTO sigl_06_data (id_owner, identifiant, label, value) "
                "VALUES (1, :identifiant, :label, :value) "
                "ON DUPLICATE KEY UPDATE label = VALUES(label)"
            ),
            {
                "identifiant": "audit_purge_months",
                "label": "Nombre de mois avant archivage de la table d'audit",
                "value": "12",
            },
        )
    except Exception as err:
        print("ERROR insert audit_purge_months,\n\terr=" + str(err))

    # Create monthly system job: audit archive + purge
    # 1st day of month at 02:00 UTC
    try:
        now = datetime.utcnow()
        # next run = next 1st day 02:00
        first_this = now.replace(day=1, hour=2, minute=0, second=0, microsecond=0)
        if now < first_this and now.day == 1:
            next_run = first_this
        else:
            # first day next month 02:00
            y = now.year + (1 if now.month == 12 else 0)
            m = 1 if now.month == 12 else now.month + 1
            next_run = now.replace(year=y, month=m, day=1, hour=2, minute=0, second=0, microsecond=0)

        params = {
            "type": "audit_purge",
            "audit": "Y"
        }

        params_json = json.dumps(params, ensure_ascii=False).replace("'", "''")
        next_run_str = next_run.strftime('%Y-%m-%d %H:%M:%S')

        conn.execute(text(f"""
            INSERT INTO automation_job (
                ajb_type, ajb_label, ajb_is_active,
                ajb_schedule_kind, ajb_schedule_time, ajb_schedule_dow,
                ajb_schedule_dom, ajb_schedule_last_dom, ajb_schedule_anchor_jan,
                ajb_fire_on, ajb_schedule_start_on, ajb_next_run_at,
                ajb_last_status, ajb_params
            ) VALUES (
                'system', 'Audit archive + purge', 'Y',
                'M', '02:00:00', NULL,
                1, 'N', 'N',
                'period_end', NULL, '{next_run_str}',
                'never', '{params_json}'
            )
        """))
    except Exception as err:
        print("ERROR insert automation_job audit_purge err=" + str(err))

    print(str(datetime.today()) + " : END of migration v3_6_10_audit_table_management revision=293f26bdbf13")


def downgrade():
    """
    No-op by design.

    This migration is intentionally irreversible per the organization's
    forward-only policy. It includes destructive operations and/or renames
    that cannot be safely undone. To roll back, restore a verified backup
    taken before revision 293f26bdbf13.
    """
    print("downgrade skipped: irreversible migration 293f26bdbf13 (forward-only policy)")
