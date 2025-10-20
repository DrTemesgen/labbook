"""v3_6_0_new_branch

Revision ID: 7ae305af7750
Revises: 469be6b8a29b
Create Date: 2025-09-17 16:20:36.945660

"""
from alembic import op
from sqlalchemy import text

from datetime import datetime

# revision identifiers, used by Alembic.
revision = '7ae305af7750'
down_revision = ('469be6b8a29b', '1a2b3c4d5e6f')  # allow upgrade from 3.5.17 or 3.5.18
branch_labels = None
depends_on = None


def _create_index_if_missing(conn, table_name, index_name, columns_sql):
    """
    Create a non-unique BTREE index if it doesn't already exist.
    columns_sql: string like "col1, col2"
    """
    check_sql = text("""
        SELECT COUNT(*) AS cnt
        FROM INFORMATION_SCHEMA.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = :table_name
          AND INDEX_NAME = :index_name
    """)
    cnt = conn.execute(check_sql, {"table_name": table_name, "index_name": index_name}).scalar()
    if cnt == 0:
        try:
            conn.execute(text(f"CREATE INDEX {index_name} ON {table_name} ({columns_sql})"))
            print(f"Created index {index_name} ON {table_name} ({columns_sql})")
        except Exception as err:
            print(f"ERROR creating index {index_name} on {table_name}: {err}")
    else:
        print(f"Index {index_name} on {table_name} already exists; skipping.")


def upgrade():
    print("--- " + str(datetime.today()) + "---")
    print("START of migration v3_6_0_new_branch revision=7ae305af7750")

    # Get the current
    conn = op.get_bind()

    # DROP TABLE list_comment (deprecated)
    try:
        conn.execute(text("DROP TABLE IF EXISTS list_comment"))
    except Exception as err:
        print("ERROR drop table list_comment,\n\terr=" + str(err))

    # ADD COLUMN for report_pwd in sigl_param_cr_data
    try:
        conn.execute(text("ALTER TABLE sigl_07_data ADD COLUMN var_in_report varchar(1) not null default 'Y'"))
    except Exception as err:
        print("ERROR add column var_in_report to sigl_07_data,\n\terr=" + str(err))

    try:
        conn.execute(text("ALTER TABLE sigl_01_data CHANGE COLUMN code code VARCHAR(50) NULL"))
    except Exception as err:
        print("ERROR alter sigl_01_data.code,\n\terr=" + str(err))

    # Rename table
    try:
        conn.execute(text("RENAME TABLE sigl_param_num_dos_data TO record_setting"))
    except Exception as err:
        print("ERROR rename table sigl_param_num_dos_data -> record_setting,\n\terr=" + str(err))

    # Rename columns + add new columns
    try:
        conn.execute(text("""
            ALTER TABLE record_setting
                CHANGE COLUMN id_data           rstg_ser       INT UNSIGNED NOT NULL AUTO_INCREMENT,
                CHANGE COLUMN id_owner          rstg_user      INT UNSIGNED NULL,
                CHANGE COLUMN sys_creation_date rstg_date      DATETIME NULL,
                CHANGE COLUMN sys_last_mod_date rstg_date_upd  DATETIME NULL,
                CHANGE COLUMN sys_last_mod_user rstg_user_upd  INT UNSIGNED NULL,
                CHANGE COLUMN periode           rstg_period    INT UNSIGNED NULL,
                CHANGE COLUMN format            rstg_format    INT UNSIGNED NULL,
                ADD COLUMN rstg_samp_mask  VARCHAR(128) NULL AFTER rstg_format,
                ADD COLUMN rstg_samp_regex VARCHAR(256) NULL AFTER rstg_samp_mask
        """))
    except Exception as err:
        print("ERROR alter table record_setting (rename/add columns),\n\terr=" + str(err))

    # ---- PERFORMANCE INDEXES FOR DHIS2 / EPIDEMIO FILTER QUERIES ----

    # sigl_02_data: filter by date + count distinct id_data
    _create_index_if_missing(conn,
                             table_name="sigl_02_data",
                             index_name="idx_rec_date_id",
                             columns_sql="rec_date_receipt, id_data")

    # sigl_05_data: (type_prel, code) used together
    _create_index_if_missing(conn,
                             table_name="sigl_05_data",
                             index_name="idx_typeprel_code",
                             columns_sql="type_prel, code")

    # sigl_09_data: (ref_variable, valeur) with range + join by id_analyse
    _create_index_if_missing(conn,
                             table_name="sigl_09_data",
                             index_name="idx_refvar_val_analyse",
                             columns_sql="ref_variable, valeur, id_analyse")

    # sigl_10_data: (id_resultat, type_validation) used together
    _create_index_if_missing(conn,
                             table_name="sigl_10_data",
                             index_name="idx_res_vld",
                             columns_sql="id_resultat, type_validation")

    # sigl_03_data: when CAT(...) filters by age/sexe for a patient
    _create_index_if_missing(conn,
                             table_name="sigl_03_data",
                             index_name="idx_patient_age_sexe",
                             columns_sql="id_data, age, sexe")

    print(str(datetime.today()) + " : END of migration v3_6_0_new_branch revision=7ae305af7750")


def downgrade():
    """
    No-op by design.

    This migration is intentionally irreversible per the organization's
    forward-only policy. It includes destructive operations and/or renames
    that cannot be safely undone. To roll back, restore a verified backup
    taken before revision 7ae305af7750.
    """
    print("downgrade skipped: irreversible migration 7ae305af7750 (forward-only policy)")
