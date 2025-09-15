"""v3_5_17_report_with_password

Revision ID: 469be6b8a29b
Revises: a6ade2bf2df6
Create Date: 2025-07-30 14:32:54.241490

"""
from alembic import op
from sqlalchemy import text

from datetime import datetime

# revision identifiers, used by Alembic.
revision = '469be6b8a29b'
down_revision = 'a6ade2bf2df6'
branch_labels = None
depends_on = None


def upgrade():
    print("--- " + str(datetime.today()) + "---")
    print("START of migration v3_5_17_report_with_password revision=469be6b8a29b")

    # Get the current
    conn = op.get_bind()

    # ADD COLUMN for report_pwd in sigl_param_cr_data
    try:
        conn.execute(text("ALTER TABLE sigl_param_cr_data ADD COLUMN report_pwd varchar(1) not null default 'N'"))
    except Exception as err:
        print("ERROR add column report_pwd to sigl_param_cr_data,\n\terr=" + str(err))

    try:
        conn.execute(text('''
            UPDATE profile_rights
            SET prr_label = REPLACE(prr_label, 'Editer', 'Éditer')
            WHERE BINARY prr_label LIKE '%Editer%'
        '''))
    except Exception as err:
        print("ERROR updating prr_label Editer -> Éditer,\n\terr=" + str(err))

    try:
        conn.execute(text('''
            UPDATE profile_rights
            SET prr_label = REPLACE(prr_label, 'Etat', 'État')
            WHERE BINARY prr_label LIKE '%Etat%'
        '''))
    except Exception as err:
        print("ERROR updating prr_label Etat -> État,\n\terr=" + str(err))

    try:
        conn.execute(text('''
            UPDATE profile_rights
            SET prr_label = REPLACE(prr_label, 'Equipement', 'Équipement')
            WHERE BINARY prr_label LIKE '%Equipement%'
        '''))
    except Exception as err:
        print("ERROR updating prr_label Equipement -> Équipement,\n\terr=" + str(err))

    try:
        conn.execute(text('''
            UPDATE profile_rights
            SET prr_label = REGEXP_REPLACE(prr_label, ' ?- ?', ' – ')
            WHERE prr_label REGEXP 'Équipement ?- ?'
        '''))
    except Exception as err:
        print("ERROR updating prr_label hyphens (REGEXP_REPLACE):\n\terr=" + str(err))

    try:
        conn.execute(text('''
            UPDATE profile_rights
            SET prr_label = REPLACE(prr_label, 'élement', 'élément')
            WHERE BINARY prr_label LIKE '%élement%'
        '''))
    except Exception as err:
        print("ERROR updating prr_label élement -> élément,\n\terr=" + str(err))

    # Create table for sending_method
    try:
        conn.execute(text('''
            create table sending_method(
            sdi_ser int unsigned AUTO_INCREMENT PRIMARY KEY,
            sdi_type varchar(1) NOT NULL,
            sdi_name varchar(100) NOT NULL,
            sdi_default varchar(1) NOT NULL DEFAULT 'N',
            sdi_date datetime,
            sdi_user int unsigned)
            character set=utf8
        '''))
    except Exception as err:
        print("ERROR create table sending_method,\n\terr=" + str(err))

    # Create table for sending_method_smtp
    try:
        conn.execute(text('''
            create table sending_method_smtp(
            sds_ser int unsigned AUTO_INCREMENT PRIMARY KEY,
            sds_sdi int unsigned DEFAULT NULL,
            sds_host varchar(255) NOT NULL,
            sds_port int unsigned NOT NULL,
            sds_username varchar(255) DEFAULT NULL,
            sds_password varbinary(1024) DEFAULT NULL,
            sds_ssl varchar(1) NOT NULL DEFAULT 'N',
            sds_starttls varchar(1) NOT NULL DEFAULT 'N',
            sds_from_email varchar(255) NOT NULL,
            sds_from_name varchar(255) DEFAULT NULL)
            character set=utf8
        '''))
    except Exception as err:
        print("ERROR create table sending_method_smtp,\n\terr=" + str(err))

    # Create table for sending_method_mailjet
    try:
        conn.execute(text('''
            create table sending_method_mailjet(
            sdm_ser int unsigned AUTO_INCREMENT PRIMARY KEY,
            sdm_sdi int unsigned DEFAULT NULL,
            sdm_api_key varbinary(1024) NOT NULL,
            sdm_api_secret varbinary(1024) NOT NULL,
            sdm_from_email varchar(255) NOT NULL,
            sdm_from_name varchar(255) DEFAULT NULL)
            character set=utf8
        '''))
    except Exception as err:
        print("ERROR create table sending_method_mailjet,\n\terr=" + str(err))

    # Create table for sending_method_whatsapp
    try:
        conn.execute(text('''
            create table sending_method_whatsapp(
            sdw_ser int unsigned AUTO_INCREMENT PRIMARY KEY,
            sdw_sdi int unsigned DEFAULT NULL,
            sdw_provider varchar(20) DEFAULT NULL,
            sdw_api_token varbinary(2048) NOT NULL,
            sdw_phone_number varchar(32) NOT NULL,
            sdw_phone_number_id varchar(64) DEFAULT NULL)
            character set=utf8
        '''))
    except Exception as err:
        print("ERROR create table sending_method_whatsapp,\n\terr=" + str(err))

    # Create table for sending_model
    try:
        conn.execute(text('''
            create table sending_model (
            mdl_ser     INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            mdl_type    VARCHAR(1) NOT NULL,
            mdl_displayname VARCHAR(100),
            mdl_name    VARCHAR(100),
            mdl_text    TEXT,
            mdl_has_attachment VARCHAR(1) NOT NULL DEFAULT 'N',
            mdl_default VARCHAR(1) NOT NULL DEFAULT 'N',
            mdl_date    DATETIME,
            mdl_user    INT UNSIGNED)
            character set=utf8
        '''))
    except Exception as err:
        print("ERROR create table sending_model,\n\terr=" + str(err))

    # Create table for sending_event
    try:
        conn.execute(text('''
            CREATE TABLE sending_event(
                sde_ser             BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                sde_date            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                sde_sent            DATETIME NULL,
                sde_user            INT UNSIGNED,
                sde_rec_num         VARCHAR(32) NOT NULL,
                sde_type            VARCHAR(1) NOT NULL,
                sde_method          INT UNSIGNED,
                sde_model           INT UNSIGNED,
                sde_recipient       VARCHAR(255) NOT NULL,
                sde_state           VARCHAR(1) NOT NULL DEFAULT 'Q',
                sde_error           TEXT,
                sde_payload         JSON NULL,
                INDEX(sde_rec_num), INDEX(sde_state), INDEX(sde_type, sde_method), INDEX(sde_provider_msgid)
            )
            CHARACTER SET=utf8
        '''))
    except Exception as err:
        print("ERROR create table sending_event,\n\terr=" + str(err))

    # ADD COLUMN for pat_agreement in sigl_03_data
    try:
        conn.execute(text("ALTER TABLE sigl_03_data ADD COLUMN pat_agreement varchar(1) not null default 'N'"))
    except Exception as err:
        print("ERROR add column pat_agreement to sigl_03_data,\n\terr=" + str(err))

    # ADD COLUMN for doc_agreement in sigl_08_data
    try:
        conn.execute(text("ALTER TABLE sigl_08_data ADD COLUMN doc_agreement varchar(1) not null default 'N'"))
    except Exception as err:
        print("ERROR add column doc_agreement to sigl_08_data,\n\terr=" + str(err))

    # Insert profile rights
    try:
        conn.execute(text('''
                          insert into profile_rights (prr_ser, prr_date, prr_by_user, prr_rank, prr_type, prr_label, prr_tag)
                          values
                          (176, NOW(), 0, 920,"RECORD","Envoyer le compte rendu", "RECORD_176"),
                          (177, NOW(), 0, 940,"RECORD","Liste des envois", "RECORD_177"),
                          (178, NOW(), 0, 7250,"SETTING","Configuration méthodes d'envoi", "SETTING_178")
                          '''))
    except Exception as err:
        print("ERROR insert new default profile_rights,\n\terr=" + str(err))

    # Insert default permissions to Y for Bio, all Tech and all Secretary and N for others
    try:
        conn.execute(text('''
                          INSERT INTO profile_permissions (prp_date, prp_by_user, prp_pro, prp_prr, prp_granted)
                          SELECT NOW(), 0, pr.pro_ser, prr.prr_ser,
                              CASE WHEN pr.pro_ser IN (2,3,4,5,6,7) THEN 'Y' ELSE 'N' END
                          FROM profile_rights AS prr
                          CROSS JOIN profile_role AS pr
                          WHERE prr.prr_ser BETWEEN 176 AND 177
                              AND NOT EXISTS (
                                  SELECT 1
                                  FROM profile_permissions pp
                                  WHERE pp.prp_pro = pr.pro_ser
                                      AND pp.prp_prr = prr.prr_ser)
                        '''))
    except Exception as err:
        print("ERROR inserting new default profile_permissions to Y for B, T, TA, TQ, S, SA\n\terr=" + str(err))

    # Insert default permissions to Y for Bio, All Tech and Secr Advanced and N for others
    try:
        conn.execute(text('''
                          INSERT INTO profile_permissions (prp_date, prp_by_user, prp_pro, prp_prr, prp_granted)
                          SELECT NOW(), 0, pr.pro_ser, prr.prr_ser,
                              CASE WHEN pr.pro_ser IN (1) THEN 'Y' ELSE 'N' END
                          FROM profile_rights AS prr
                          CROSS JOIN profile_role AS pr
                          WHERE prr.prr_ser BETWEEN 178 AND 178
                              AND NOT EXISTS (
                                  SELECT 1
                                  FROM profile_permissions pp
                                  WHERE pp.prp_pro = pr.pro_ser
                                      AND pp.prp_prr = prr.prr_ser)
                        '''))
    except Exception as err:
        print("ERROR inserting new default profile_permissions to Y for B, T, TA, TQ , SA\n\terr=" + str(err))

    print(str(datetime.today()) + " : END of migration v3_5_17_report_with_password revision=469be6b8a29b")


def downgrade():
    pass
