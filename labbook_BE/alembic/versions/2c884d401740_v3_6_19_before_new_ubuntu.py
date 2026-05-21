"""v3_6_19_before_new_ubuntu

Revision ID: 2c884d401740
Revises: ef1f9f565b91
Create Date: 2026-04-29 14:46:52.022006

"""
from alembic import op
from sqlalchemy import text
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '2c884d401740'
down_revision = 'ef1f9f565b91'
branch_labels = None
depends_on = None


OWNER_ID = 1


def create_analysis(conn, owner_id, analysis_def, vars_def, links_def):
    var_ids = {}

    for v in vars_def:
        if isinstance(v["type_resultat"], str):
            row_type = conn.execute(text("""
                SELECT id_data FROM sigl_dico_data
                WHERE dico_name = 'type_resultat' AND label = :label LIMIT 1"""), {"label": v["type_resultat"]}).fetchone()

            if not row_type:
                print("ERROR type_resultat not found,\n\ttype_resultat=" + str(v["type_resultat"]))
                continue

            type_resultat = row_type.id_data
        else:
            type_resultat = v["type_resultat"]

        res = conn.execute(text("""
            INSERT INTO sigl_07_data (
                id_owner, libelle, description, unite, normal_min, normal_max, commentaire,
                type_resultat, unite2, formule_unite2, formule, accuracy, precision2,
                code_var, var_highlight, var_show_minmax, var_in_report
            )
            VALUES (
                :id_owner, :libelle, '', :unite, :normal_min, :normal_max, '',
                :type_resultat, 0, '', '', :accuracy, 0, :code_var, 'N', 'N', 'Y'
            )
            ON DUPLICATE KEY UPDATE id_data = LAST_INSERT_ID(id_data)"""), {
            "id_owner": owner_id, "libelle": v["libelle"], "unite": v["unite"], "normal_min": v["normal_min"],
            "normal_max": v["normal_max"], "type_resultat": type_resultat, "accuracy": v["accuracy"],
            "code_var": v["code_var"]})

        var_ids[v["code_var"]] = res.lastrowid

    row = conn.execute(text("""
        SELECT id_data FROM sigl_05_data
        WHERE id_owner = :id_owner AND code = :code
        LIMIT 1"""), {"id_owner": owner_id, "code": analysis_def["code"]}).fetchone()

    if row:
        ana_id = row.id_data

    else:
        res = conn.execute(text("""
            INSERT INTO sigl_05_data (
                id_owner, code, nom, abbr, famille, cote_unite, cote_valeur,
                commentaire, produit_biologique, type_prel, type_analyse,
                actif, ana_whonet, ana_ast, ana_loinc, ana_lite
            )
            VALUES (
                :id_owner, :code, :nom, :abbr, :famille, :cote_unite, :cote_valeur,
                :commentaire, :produit_biologique, :type_prel, :type_analyse,
                4, 5, 'N', :ana_loinc, 'N'
            )
        """), {
            "id_owner": owner_id,
            "code": analysis_def["code"],
            "nom": analysis_def["nom"],
            "abbr": analysis_def["abbr"],
            "famille": analysis_def["famille"],
            "cote_unite": analysis_def["cote_unite"],
            "cote_valeur": analysis_def["cote_valeur"],
            "commentaire": analysis_def["commentaire"],
            "produit_biologique": analysis_def["produit_biologique"],
            "type_prel": analysis_def["type_prel"],
            "type_analyse": analysis_def["type_analyse"],
            "ana_loinc": analysis_def["ana_loinc"],
        })

        ana_id = res.lastrowid

    for code_var, position, num_var in links_def:
        id_refvariable = var_ids.get(code_var)

        if not id_refvariable:
            continue

        existing = conn.execute(text("""
            SELECT id_data FROM sigl_05_07_data
            WHERE id_owner = :id_owner AND id_refanalyse = :id_refanalyse AND id_refvariable = :id_refvariable
            LIMIT 1"""), {"id_owner": owner_id, "id_refanalyse": ana_id, "id_refvariable": id_refvariable}).fetchone()

        if existing:
            continue

        conn.execute(text("""
            INSERT INTO sigl_05_07_data (
                id_owner, id_refanalyse, id_refvariable, position, num_var, obligatoire, var_whonet, var_qrcode
            )
            VALUES (
                :id_owner, :id_refanalyse, :id_refvariable, :position, :num_var, 4, 5, 'N'
            )"""), {"id_owner": owner_id, "id_refanalyse": ana_id, "id_refvariable": id_refvariable,
                    "position": position, "num_var": num_var})


def upgrade():
    print("--- " + str(datetime.today()) + "---")
    print("START of migration v3_6_19_before_new_ubuntu revision=2c884d401740")

    conn = op.get_bind()

    # Add pat_amicare column (AmiCare patient ID)
    try:
        conn.execute(text("""ALTER TABLE sigl_03_data ADD COLUMN pat_amicare INT UNSIGNED NOT NULL DEFAULT 0"""))
    except Exception as err:
        print("ERROR add column pat_amicare in sigl_03_data,\n\terr=" + str(err))

    # Add DET and DSQU dictionaries
    try:
        conn.execute(text("""
            INSERT IGNORE INTO sigl_dico_data (
                id_owner, dico_name, label, short_label, position, code, dico_descr, dict_formatting
            )
            VALUES
                (1, 'DET', 'Détecté', 'det', 10, 'det', 'Détecté - Non détecté', 'N'),
                (1, 'DET', 'Non détecté', 'ndet', 20, 'ndet', 'Détecté - Non détecté', 'N'),
                (1, 'DET', 'Indéterminé', 'idet', 30, 'idet', 'Détecté - Non détecté', 'N'),

                (1, 'DSQU', 'Négatif', 'neg', 10, 'neg', 'Valeurs utilisées pour les examens urinaires', 'N'),
                (1, 'DSQU', 'Trace', 'trac', 20, 'trac', 'Valeurs utilisées pour les examens urinaires', 'N'),
                (1, 'DSQU', '0', 'P1', 30, 'P1', 'Valeurs utilisées pour les examens urinaires', 'N'),
                (1, 'DSQU', '++', 'P2', 40, 'P2', 'Valeurs utilisées pour les examens urinaires', 'N'),
                (1, 'DSQU', '+++', 'P3', 50, 'P3', 'Valeurs utilisées pour les examens urinaires', 'N'),
                (1, 'DSQU', '++++', 'P4', 60, 'P4', 'Valeurs utilisées pour les examens urinaires', 'N')
        """))
    except Exception as err:
        print("ERROR insert DET/DSQU dictionaries,\n\terr=" + str(err))

    # Add values to existing dictionaries
    try:
        conn.execute(text("""
            INSERT IGNORE INTO sigl_dico_data (
                id_owner, dico_name, label, short_label, position, code, dico_descr, dict_formatting
            )
            VALUES
                (1, 'posneg', 'Normal', 'normal', 30, 'normal', '', 'N'),
                (1, 'posneg', 'Elevé', 'eleve', 40, 'eleve', '', 'N'),
                (1, 'vih', 'Double réactivité', 'Dreactive', 80, 'Dreactive', '', 'N')
        """))
    except Exception as err:
        print("ERROR insert values into existing dictionaries,\n\terr=" + str(err))

    # Add DET and DSQU type_resultat
    try:
        conn.execute(text("""
            INSERT IGNORE INTO sigl_dico_data (
                id_owner, dico_name, label, short_label, position, code, dico_descr, dict_formatting
            )
            VALUES
                (1, 'type_resultat', 'DET', 'DET', 380, 'DET', '', 'N'),
                (1, 'type_resultat', 'DSQU', 'DSQU', 390, 'DSQU', '', 'N')
        """))
    except Exception as err:
        print("ERROR insert DET/DSQU type_resultat,\n\terr=" + str(err))

    # --- MPOX ---
    try:
        analysis_def = {
            "code": "MPOX", "nom": "Recherche de MPOX", "abbr": "MPOX",
            "famille": 302, "cote_unite": "B", "cote_valeur": 0,
            "commentaire": "Recherche de MPOX par PCR en temps réel",
            "produit_biologique": 1, "type_prel": 138,
            "type_analyse": 170, "ana_loinc": "100383-9"
        }

        vars_def = [
            {"code_var": "906", "libelle": "MPOX", "unite": 0, "normal_min": "", "normal_max": "", "type_resultat": "DET", "accuracy": 0},
            {"code_var": "907", "libelle": "Valeur Ct MPOX", "unite": 0, "normal_min": "18.5", "normal_max": "40", "type_resultat": 228, "accuracy": 1},
            {"code_var": "908", "libelle": "Interprétation", "unite": 0, "normal_min": "", "normal_max": "", "type_resultat": "DET", "accuracy": 0},
            {"code_var": "909", "libelle": "Commentaire", "unite": 0, "normal_min": "", "normal_max": "", "type_resultat": 226, "accuracy": 0},
        ]

        links_def = [("906", 10, 1), ("907", 20, 2), ("908", 30, 3), ("909", 40, 4)]

        create_analysis(conn, OWNER_ID, analysis_def, vars_def, links_def)

    except Exception as err:
        print("ERROR create analysis MPOX,\n\terr=" + str(err))

    # --- TASO ---
    try:
        analysis_def = {
            "code": "TASO", "nom": "Taux d’Antistreptolysines O", "abbr": "",
            "famille": 302, "cote_unite": "B", "cote_valeur": 0,
            "commentaire": "Dosage des anticorps antistreptolysine O",
            "produit_biologique": 1, "type_prel": 138,
            "type_analyse": 170, "ana_loinc": "5370-2"
        }

        vars_def = [
            {"code_var": "903", "libelle": "TASO / ASLO", "unite": 0, "normal_min": "", "normal_max": "", "type_resultat": 228, "accuracy": 2},
            {"code_var": "904", "libelle": "Commentaire", "unite": 0, "normal_min": "", "normal_max": "", "type_resultat": 226, "accuracy": 0},
            {"code_var": "905", "libelle": "Interprétation", "unite": 0, "normal_min": "", "normal_max": "", "type_resultat": 230, "accuracy": 0},
        ]

        links_def = [("903", 20, 1), ("904", 30, 2), ("905", 40, 3)]

        create_analysis(conn, OWNER_ID, analysis_def, vars_def, links_def)

    except Exception as err:
        print("ERROR create analysis TASO,\n\terr=" + str(err))

    # --- VHAG ---
    try:
        analysis_def = {
            "code": "VHAG", "nom": "Antigène du Virus de l’Hépatite C", "abbr": "",
            "famille": 302, "cote_unite": "B", "cote_valeur": 0,
            "commentaire": "Recherche de l’antigène du virus de l’hépatite C",
            "produit_biologique": 1, "type_prel": 138,
            "type_analyse": 170, "ana_loinc": "11011-4"
        }

        vars_def = [
            {"code_var": "901", "libelle": "Antigène VHC", "unite": 0, "normal_min": "", "normal_max": "", "type_resultat": 230, "accuracy": 0},
            {"code_var": "902", "libelle": "Commentaire", "unite": 0, "normal_min": "", "normal_max": "", "type_resultat": 226, "accuracy": 0},
        ]

        links_def = [("901", 10, 1), ("902", 20, 2)]

        create_analysis(conn, OWNER_ID, analysis_def, vars_def, links_def)

    except Exception as err:
        print("ERROR create analysis VHAG,\n\terr=" + str(err))

    # --- VIHS ---
    try:
        analysis_def = {
            "code": "VIHS", "nom": "Sérologie VIH", "abbr": "",
            "famille": 302, "cote_unite": "B", "cote_valeur": 0,
            "commentaire": "Test immunologique du VIH",
            "produit_biologique": 1, "type_prel": 138,
            "type_analyse": 170, "ana_loinc": "56888-1"
        }

        vars_def = [
            {"code_var": "917", "libelle": "Determine VIH", "unite": 0, "normal_min": "", "normal_max": "", "type_resultat": 625, "accuracy": 0},
            {"code_var": "918", "libelle": "Bioline VIH", "unite": 0, "normal_min": "", "normal_max": "", "type_resultat": 625, "accuracy": 0},
            {"code_var": "919", "libelle": "Type VIH", "unite": 0, "normal_min": "", "normal_max": "", "type_resultat": 625, "accuracy": 0},
            {"code_var": "920", "libelle": "Interprétation finale", "unite": 0, "normal_min": "", "normal_max": "", "type_resultat": "DET", "accuracy": 0},
        ]

        links_def = [("917", 10, 1), ("918", 20, 2), ("919", 30, 3), ("920", 40, 4)]

        create_analysis(conn, OWNER_ID, analysis_def, vars_def, links_def)

    except Exception as err:
        print("ERROR create analysis VIHS,\n\terr=" + str(err))

    # --- EPHU ---
    try:
        analysis_def = {
            "code": "EPHU", "nom": "Examen physico-chimique des urines", "abbr": "EPHU",
            "famille": 12, "cote_unite": "", "cote_valeur": 0,
            "commentaire": "Analyse physico-chimique des urines par bandelette",
            "produit_biologique": 3, "type_prel": 153,
            "type_analyse": 170, "ana_loinc": "24357-6"
        }

        vars_def = [
            {"code_var": "888", "libelle": "Aspect", "unite": 0, "normal_min": "", "normal_max": "", "type_resultat": "DSQU", "accuracy": 0},
            {"code_var": "889", "libelle": "Couleur", "unite": 0, "normal_min": "", "normal_max": "", "type_resultat": "DSQU", "accuracy": 0},
            {"code_var": "890", "libelle": "Densité urinaire", "unite": 0, "normal_min": "1.005", "normal_max": "1.035", "type_resultat": 228, "accuracy": 3},
            {"code_var": "891", "libelle": "pH urinaire", "unite": 0, "normal_min": "4.5", "normal_max": "8.0", "type_resultat": 228, "accuracy": 0},
            {"code_var": "892", "libelle": "Leucocytes", "unite": 0, "normal_min": "", "normal_max": "", "type_resultat": "DSQU", "accuracy": 0},
            {"code_var": "893", "libelle": "Albumine", "unite": 0, "normal_min": "", "normal_max": "", "type_resultat": "DSQU", "accuracy": 0},
            {"code_var": "894", "libelle": "Glucose urinaire", "unite": 0, "normal_min": "", "normal_max": "", "type_resultat": "DSQU", "accuracy": 0},
            {"code_var": "895", "libelle": "Acétone", "unite": 0, "normal_min": "", "normal_max": "", "type_resultat": "DSQU", "accuracy": 0},
            {"code_var": "896", "libelle": "Urobilinogène", "unite": 0, "normal_min": "", "normal_max": "", "type_resultat": "DSQU", "accuracy": 0},
            {"code_var": "897", "libelle": "Hémoglobine", "unite": 0, "normal_min": "", "normal_max": "", "type_resultat": "DSQU", "accuracy": 0},
            {"code_var": "898", "libelle": "Bilirubine", "unite": 0, "normal_min": "", "normal_max": "", "type_resultat": "DSQU", "accuracy": 0},
            {"code_var": "899", "libelle": "Nitrites", "unite": 0, "normal_min": "", "normal_max": "", "type_resultat": 230, "accuracy": 0},
            {"code_var": "900", "libelle": "Acide ascorbique", "unite": 0, "normal_min": "", "normal_max": "", "type_resultat": "DSQU", "accuracy": 0},
        ]

        links_def = [("888", 20, 1), ("889", 20, 2), ("890", 30, 3), ("891", 40, 4), ("892", 50, 5), ("893", 60, 6),
                     ("894", 70, 7), ("895", 80, 8), ("896", 90, 9), ("897", 100, 10), ("898", 110, 11), ("899", 120, 12),
                     ("900", 130, 13)]

        create_analysis(conn, OWNER_ID, analysis_def, vars_def, links_def)

    except Exception as err:
        print("ERROR create analysis EPHU,\n\terr=" + str(err))

    # ask for update translation in DB
    try:
        # insert a line in init_version
        conn.execute(text("insert into init_version (ini_date, ini_stat) values (NOW(), 'Y')"))
    except Exception as err:
        print("ERROR insert init_version,\n\terr=" + str(err))

    print(str(datetime.today()) + " : END of migration v3_6_19_before_new_ubuntu revision=2c884d401740")


def downgrade():
    """
    No-op by design.

    This migration is intentionally irreversible per the organization's
    forward-only policy. It includes destructive operations and/or renames
    that cannot be safely undone. To roll back, restore a verified backup
    taken before revision 2c884d401740.
    """
    print("downgrade skipped: irreversible migration 2c884d401740 (forward-only policy)")
