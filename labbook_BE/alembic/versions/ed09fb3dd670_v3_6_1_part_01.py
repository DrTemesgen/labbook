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

    print(str(datetime.today()) + " : END of migration v3_6_1_part_01 revision=ed09fb3dd670")


def downgrade():
    pass
