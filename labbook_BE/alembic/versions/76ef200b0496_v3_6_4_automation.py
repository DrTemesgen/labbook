"""v3_6_4_automation

Revision ID: 76ef200b0496
Revises: 34428139a224
Create Date: 2025-10-23 14:19:39.269888

"""
from alembic import op
from sqlalchemy import text

from datetime import datetime


# revision identifiers, used by Alembic.
revision = '76ef200b0496'
down_revision = '34428139a224'
branch_labels = None
depends_on = None


def upgrade():
    print("--- " + str(datetime.today()) + "---")
    print("START of migration v3_6_4_automation revision=76ef200b0496")

    # Get the current
    conn = op.get_bind()

    # COPY alembic resource, erase file only if more recent
    try:
        from distutils.dir_util import copy_tree

        fromDirectory = "alembic/resource"
        toDirectory = "/storage/resource"

        copy_tree(fromDirectory, toDirectory, update=1)
    except Exception as err:
        print("ERROR copy alembic resource,\n\terr=" + str(err))

    # ADD template billing status
    try:
        conn.execute(text("insert into template_setting "
                          "(tpl_date, tpl_name, tpl_file, tpl_default, tpl_type) "
                          "values (NOW(), 'Modèle état de la facturation', 'tpl_billing_status.odt', 'Y', 'BIL')"))
    except Exception as err:
        print("ERROR insert billing status template for template_setting,\n\terr=" + str(err))

    # Insert profile rights
    try:
        conn.execute(text('''
                          insert into profile_rights (prr_ser, prr_date, prr_by_user, prr_rank, prr_type, prr_label, prr_tag)
                          values
                          (179, NOW(), 0, 31000,"AUTO","Configuration des automatismes", "AUTO_179"),
                          (180, NOW(), 0, 31020,"AUTO","Ajouter un élément", "AUTO_180"),
                          (181, NOW(), 0, 31040,"AUTO","Éditer un élément", "AUTO_181"),
                          (182, NOW(), 0, 31060,"AUTO","Supprimer un élément", "AUTO_182")
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
                          WHERE prr.prr_ser BETWEEN 179 AND 182
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
                          WHERE prr.prr_ser BETWEEN 179 AND 182
                        '''))
    except Exception as err:
        print("ERROR inserting new default profile_permissions to N for others,\n\terr=" + str(err))

    # Normalizing multiple spaces in sigl_05_data.nom
    try:
        conn.execute(text("""
            UPDATE sigl_05_data
            SET nom = REGEXP_REPLACE(nom, ' {2,}', ' ')
            WHERE nom REGEXP ' {2,}'
        """))
    except Exception as err:
        print("ERROR normalize spaces in sigl_05_data.nom,\n\terr=" + str(err))

    # sigl_05_data.commentaire
    try:
        print("Normalizing multiple spaces in sigl_05_data.commentaire ...")
        conn.execute(text("""
            UPDATE sigl_05_data
            SET commentaire = REGEXP_REPLACE(commentaire, ' {2,}', ' ')
            WHERE commentaire REGEXP ' {2,}'
        """))
    except Exception as err:
        print("ERROR normalize spaces in sigl_05_data.commentaire,\n\terr=" + str(err))

    # sigl_dico_data.label
    try:
        print("Normalizing multiple spaces in sigl_dico_data.label ...")
        conn.execute(text("""
            UPDATE sigl_dico_data
            SET label = REGEXP_REPLACE(label, ' {2,}', ' ')
            WHERE label REGEXP ' {2,}'
        """))
    except Exception as err:
        print("ERROR normalize spaces in sigl_dico_data.label,\n\terr=" + str(err))

    # sigl_07_data.libelle
    try:
        print("Normalizing multiple spaces in sigl_07_data.libelle ...")
        conn.execute(text("""
            UPDATE sigl_07_data
            SET libelle = REGEXP_REPLACE(libelle, ' {2,}', ' ')
            WHERE libelle REGEXP ' {2,}'
        """))
    except Exception as err:
        print("ERROR normalize spaces in sigl_07_data.libelle,\n\terr=" + str(err))

    # sigl_07_data.commentaire
    try:
        print("Normalizing multiple spaces in sigl_07_data.commentaire ...")
        conn.execute(text("""
            UPDATE sigl_07_data
            SET commentaire = REGEXP_REPLACE(commentaire, ' {2,}', ' ')
            WHERE commentaire REGEXP ' {2,}'
        """))
    except Exception as err:
        print("ERROR normalize spaces in sigl_07_data.commentaire,\n\terr=" + str(err))

    # Cleanup espaces multiples dans translations.tra_text
    try:
        conn.execute(text("""
            UPDATE translations
            SET tra_text = REGEXP_REPLACE(tra_text, ' {2,}', ' ')
            WHERE tra_text REGEXP ' {2,}';
        """))
    except Exception as err:
        print("ERROR cleanup translations.tra_text (multiple spaces): " + str(err))

    try:
        conn.execute(text("""
            CREATE TABLE automation_job (
              ajb_ser INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
              ajb_type ENUM('dhis2','activity','billing') NOT NULL,
              ajb_label VARCHAR(120) NOT NULL,
              ajb_is_active VARCHAR(1) NOT NULL DEFAULT 'Y',
              ajb_schedule_kind ENUM('D','W','M','B','T','Q','S','A') NOT NULL,
              ajb_schedule_time TIME NOT NULL DEFAULT '02:00:00',
              ajb_schedule_dow TINYINT UNSIGNED NULL,
              ajb_schedule_dom TINYINT UNSIGNED NULL,
              ajb_schedule_last_dom VARCHAR(1) NOT NULL DEFAULT 'N',
              ajb_schedule_anchor_jan VARCHAR(1) NOT NULL DEFAULT 'Y',
              ajb_fire_on ENUM('period_end','period_start') NOT NULL DEFAULT 'period_end',
              ajb_schedule_start_on DATE NULL,
              ajb_next_run_at DATETIME NOT NULL,
              ajb_last_run_at DATETIME NULL,
              ajb_last_status ENUM('never','running','success','error','timeout') NOT NULL DEFAULT 'never',
              ajb_params JSON NOT NULL,
              ajb_created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
              ajb_updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              INDEX idx_ajb_due (ajb_is_active, ajb_next_run_at),
              INDEX idx_ajb_type (ajb_type),
              INDEX idx_ajb_sched (ajb_schedule_kind, ajb_schedule_time)
            ) CHARACTER SET=utf8
        """))
    except Exception as err:
        print("ERROR create table automation_job,\n\terr=" + str(err))

    try:
        conn.execute(text("""
            CREATE TABLE automation_run (
              arn_ser INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
              arn_job_id INT UNSIGNED NOT NULL,
              arn_started_at DATETIME NOT NULL,
              arn_finished_at DATETIME NULL,
              arn_status ENUM('running','success','error','timeout') NOT NULL,
              arn_output_uri VARCHAR(1024) NULL,
              arn_rows_count INT NULL,
              arn_message VARCHAR(1000) NULL,
              arn_error_trace MEDIUMTEXT NULL,
              INDEX idx_arn_job_started (arn_job_id, arn_started_at)
            ) CHARACTER SET=utf8
        """))
    except Exception as err:
        print("ERROR create table automation_run,\n\terr=" + str(err))

    print(str(datetime.today()) + " : END of migration v3_6_4_automation revision=76ef200b0496")


def downgrade():
    """
    No-op by design.

    This migration is intentionally irreversible per the organization's
    forward-only policy. It includes destructive operations and/or renames
    that cannot be safely undone. To roll back, restore a verified backup
    taken before revision 76ef200b0496.
    """
    print("downgrade skipped: irreversible migration 76ef200b0496 (forward-only policy)")
