"""v3_6_1_part_01

Revision ID: ed09fb3dd670
Revises: 7ae305af7750
Create Date: 2025-09-26 16:56:03.278018

"""
from alembic import op
from sqlalchemy import text

from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'ed09fb3dd670'
down_revision = '7ae305af7750'
branch_labels = None
depends_on = None


def upgrade():
    print("--- " + str(datetime.today()) + "---")
    print("START of migration v3_6_1_part_01 revision=ed09fb3dd670")

    # Get the current
    conn = op.get_bind()

    # Add column eqp_status
    try:
        conn.execute(text("ALTER TABLE sigl_equipement_data ADD COLUMN eqp_status INT UNSIGNED NOT NULL DEFAULT 0"))
    except Exception as err:
        print("ERROR add column eqp_status to sigl_equipement_data,\n\terr=" + str(err))

    # Optional index for faster filtering/sorting by status
    try:
        conn.execute(text("CREATE INDEX idx_equipement_eqp_status ON sigl_equipement_data (eqp_status)"))
    except Exception as err:
        print("ERROR create index idx_equipement_eqp_status,\n\terr=" + str(err))

    # insert equipment status dictionary
    try:
        conn.execute(text("""
            INSERT INTO sigl_dico_data
            (id_owner, dico_name, label, short_label, position, code, dict_formatting) VALUES
            (0, 'etat_equipement', 'Fonctionnel', 'OK', 1, 'eqp_stat1', 'N'),
            (0, 'etat_equipement', 'Non fonctionnel', 'Non fonct.', 2, 'eqp_stat2', 'N'),
            (0, 'etat_equipement', 'En panne (en attente de réparation)', 'Panne (att. rep.)', 3, 'eqp_stat3', 'N'),
            (0, 'etat_equipement', 'Endommagé', 'Endommagé', 4, 'eqp_stat4', 'N'),
            (0, 'etat_equipement', 'Défectueux', 'Défectueux', 5, 'eqp_stat5', 'N'),
            (0, 'etat_equipement', 'En maintenance', 'Maintenance', 6, 'eqp_stat6', 'N'),
            (0, 'etat_equipement', 'Obsolète / Mis au rebut', 'Obsolète/Rebut', 7, 'eqp_stat7', 'N'),
            (0, 'etat_equipement', 'En stock / Réservé', 'Stock/Réservé', 8, 'eqp_stat8', 'N')
        """))
    except Exception as err:
        print("ERROR insert 8 equipment status dictionary,\n\terr=" + str(err))

    # --- OAUTH2 CLIENTS ----------------------------------------------------------
    try:
        conn.execute(text("""
            CREATE TABLE oauth2_client (
              oacl_ser INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
              oacl_client_id VARCHAR(128) NOT NULL,
              oacl_client_secret VARCHAR(256) NOT NULL DEFAULT '',
              oacl_client_name VARCHAR(255) NOT NULL DEFAULT '',
              oacl_user_id INT UNSIGNED NOT NULL DEFAULT 0,
              oacl_redirect_uris TEXT NOT NULL,
              oacl_scope TEXT NOT NULL,
              oacl_grant_types VARCHAR(255) NOT NULL DEFAULT 'authorization_code refresh_token client_credentials',
              oacl_response_types VARCHAR(255) NOT NULL DEFAULT 'code',
              oacl_token_endpoint_auth_method VARCHAR(50) NOT NULL DEFAULT 'client_secret_basic',
              oacl_is_active VARCHAR(1) NOT NULL DEFAULT 'Y',
              oacl_created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
              oacl_updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              UNIQUE KEY uq_oacl_client_id (oacl_client_id),
              KEY idx_oacl_user (oacl_user_id)
            ) CHARACTER SET=utf8
        """))
    except Exception as err:
        print("ERROR create table oauth2_client,\n\terr=" + str(err))
    
    # --- OAUTH2 TOKENS ---
    try:
        conn.execute(text("""
            CREATE TABLE oauth2_token (
              oato_ser INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
              oato_client_id VARCHAR(128) NOT NULL,
              oato_token_type VARCHAR(40) NOT NULL DEFAULT 'Bearer',
              oato_access_token VARCHAR(512) NOT NULL,
              oato_refresh_token VARCHAR(512) NULL,
              oato_scope TEXT NULL,
              oato_revoked VARCHAR(1) NOT NULL DEFAULT 'N',
              oato_issued_at INT UNSIGNED NOT NULL,
              oato_expires_in INT UNSIGNED NOT NULL,
              oato_created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
              KEY idx_oato_access (oato_access_token(191)),
              KEY idx_oato_refresh (oato_refresh_token(191)),
              KEY idx_oato_client (oato_client_id)
            ) CHARACTER SET=utf8
        """))
    except Exception as err:
        print("ERROR create table oauth2_token,\n\terr=" + str(err))
    
    # --- OAUTH2 AUTHORIZATION CODES (PKCE) ---
    try:
        conn.execute(text("""
            CREATE TABLE oauth2_code (
              oaco_ser INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
              oaco_code VARCHAR(255) NOT NULL,
              oaco_client_id VARCHAR(128) NOT NULL,
              oaco_redirect_uri VARCHAR(512) NOT NULL DEFAULT '',
              oaco_scope TEXT NULL,
              oaco_auth_time INT UNSIGNED NOT NULL DEFAULT 0,
              oaco_nonce VARCHAR(255) NOT NULL DEFAULT '',
              oaco_code_challenge VARCHAR(255) NOT NULL DEFAULT '',
              oaco_code_challenge_method VARCHAR(10) NOT NULL DEFAULT '',
              oaco_expires_at INT UNSIGNED NOT NULL,
              oaco_created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
              UNIQUE KEY uq_oaco_code (oaco_code),
              KEY idx_oaco_client (oaco_client_id)
            ) CHARACTER SET=utf8
        """))
    except Exception as err:
        print("ERROR create table oauth2_code,\n\terr=" + str(err))
    
    # --- LabBook FE ---
    try:
        conn.execute(text("""
            INSERT INTO oauth2_client (
              oacl_client_id,
              oacl_client_secret,
              oacl_client_name,
              oacl_user_id,
              oacl_redirect_uris,
              oacl_scope,
              oacl_grant_types,
              oacl_token_endpoint_auth_method,
              oacl_is_active
            ) VALUES (
              'labbook-FE',
              '',
              'LabBook Front-End',
              0,
              '/oauth/callback',
              '',
              'authorization_code refresh_token',
              'none',
              'Y'
            )
        """))
    except Exception as err:
        print("ERROR insert oauth2_client (FE),\n\terr=" + str(err))

    print(str(datetime.today()) + " : END of migration v3_6_1_part_01 revision=ed09fb3dd670")


def downgrade():
    """
    No-op by design.

    This migration is intentionally irreversible per the organization's
    forward-only policy. It includes destructive operations and/or renames
    that cannot be safely undone. To roll back, restore a verified backup
    taken before revision ed09fb3dd670.
    """
    print("downgrade skipped: irreversible migration ed09fb3dd670 (forward-only policy)")
