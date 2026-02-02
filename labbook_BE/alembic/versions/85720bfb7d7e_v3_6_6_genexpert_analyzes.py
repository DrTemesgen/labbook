"""v3_6_6_genexpert_analyzes

Revision ID: 85720bfb7d7e
Revises: 8a8f1ca60adc
Create Date: 2025-11-25 14:32:49.461279

"""
from alembic import op
from sqlalchemy import text
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '85720bfb7d7e'
down_revision = '8a8f1ca60adc'
branch_labels = None
depends_on = None


def upgrade():
    print("--- " + str(datetime.today()) + "---")
    print("START of migration v3_6_6_genexpert_analyzes revision=85720bfb7d7e")

    conn = op.get_bind()

    # Insert new types of sample
    try:
        conn.execute(text(
            'insert into sigl_dico_data (id_owner, dico_name, label, short_label, position, code) '
            'values (1, "type_prel", "Écouvillon nasopharyngé", "nasopharyngé", 1346, "nasophar")'
        ))
    except Exception as err:
        print("ERROR insert type of sample Écouvillon nasopharyngé,\n\terr=" + str(err))

    try:
        conn.execute(text(
            'insert into sigl_dico_data (id_owner, dico_name, label, short_label, position, code) '
            'values (1, "type_prel", "Écouvillon oropharyngé", "oropharyngé", 1347, "orophar")'
        ))
    except Exception as err:
        print("ERROR insert type of sample Écouvillon oropharyngé,\n\terr=" + str(err))

    try:
        conn.execute(text(
            'insert into sigl_dico_data (id_owner, dico_name, label, short_label, position, code) '
            'values (1, "type_prel", "Écouvillon nasal", "nasal", 1348, "nasal")'
        ))
    except Exception as err:
        print("ERROR insert type of sample Écouvillon nasal,\n\terr=" + str(err))

    # Create variables
    vars_def = [
        {"key": "IMP1",         "libelle": "IMP1",                         "code_var": "821"},
        {"key": "KPC",          "libelle": "KPC",                          "code_var": "822"},
        {"key": "NDM",          "libelle": "NDM",                          "code_var": "823"},
        {"key": "OXA48",        "libelle": "OXA48",                        "code_var": "824"},
        {"key": "VIM",          "libelle": "VIM",                          "code_var": "825"},
        {"key": "HBV_VL",       "libelle": "Xpert HBV Viral Load",         "code_var": "826"},
        {"key": "HIV1",         "libelle": "HIV-1",                        "code_var": "827"},
        {"key": "QC",           "libelle": "QC",                           "code_var": "828"},
        {"key": "HIV1_VL_XC",   "libelle": "Xpert HIV-1 Viral Load XC",    "code_var": "829"},
        {"key": "MTB",          "libelle": "MTB",                          "code_var": "830"},
        {"key": "MTB_TRACE",    "libelle": "MTB Trace",                    "code_var": "831"},
        {"key": "RIF_RES",      "libelle": "RIF Resistance",               "code_var": "832"},
        {"key": "SC2",          "libelle": "Xpert Xpress SARS-CoV-2",      "code_var": "833"},
        {"key": "IMP",          "libelle": "IMP",                          "code_var": "834"},
        {"key": "HIV1_VL",      "libelle": "Xpert_HIV-1 Viral Load",       "code_var": "835"},
    ]

    var_ids = {}

    for v in vars_def:
        libelle = v["libelle"]
        csv_code_var = v["code_var"]

        # 1) Try by libelle
        row = conn.execute(
            text(
                """
                SELECT id_data, code_var
                FROM sigl_07_data
                WHERE id_owner = 1 AND libelle = :libelle
                LIMIT 1
                """
            ),
            {"libelle": libelle},
        ).fetchone()

        if row:
            var_ids[v["key"]] = row.id_data
            continue

        # 2) Check if the CSV code_var is already used
        row_code = conn.execute(
            text(
                """
                SELECT id_data
                FROM sigl_07_data
                WHERE code_var = :code_var
                LIMIT 1
                """
            ),
            {"code_var": csv_code_var},
        ).fetchone()

        if row_code:
            # 3) If already used, get the max numeric code_var and increment
            max_row = conn.execute(
                text(
                    """
                    SELECT MAX(CAST(code_var AS UNSIGNED)) AS max_code
                    FROM sigl_07_data
                    WHERE code_var REGEXP '^[0-9]+$'
                    """
                )
            ).fetchone()
            max_code = max_row.max_code if max_row and max_row.max_code is not None else 0
            code_var_to_use = str(int(max_code) + 1)
        else:
            # CSV code is free, use it as-is
            code_var_to_use = csv_code_var

        res = conn.execute(
            text(
                """
                INSERT INTO sigl_07_data
                (id_owner,
                 libelle,
                 description,
                 unite,
                 normal_min,
                 normal_max,
                 commentaire,
                 type_resultat,
                 unite2,
                 formule_unite2,
                 formule,
                 accuracy,
                 precision2,
                 code_var,
                 var_highlight,
                 var_show_minmax,
                 var_in_report)
                VALUES
                (
                 1,
                 :libelle,
                 '',
                 0,
                 '',
                 '',
                 '',
                 226,
                 0,
                 '',
                 '',
                 0,
                 0,
                 :code_var,
                 'N',
                 'N',
                 'Y'
                )
                """
            ),
            {
                "libelle": libelle,
                "code_var": code_var_to_use,
            },
        )

        new_id = res.lastrowid
        var_ids[v["key"]] = new_id

    # Helper for type_prel from dictionary
    def get_type_prel_id_by_code(dico_code):
        row = conn.execute(
            text(
                """
                SELECT id_data
                FROM sigl_dico_data
                WHERE dico_name = 'type_prel' AND code = :code
                LIMIT 1
                """
            ),
            {"code": dico_code},
        ).fetchone()
        if not row:
            print("ERROR missing type_prel code=" + dico_code)
            return None
        return row.id_data

    # Create analyses (type_prel resolved by dico code, produit_biologique = 0)
    analyses_def = [
        {
            "key": "GX01",
            "code": "GX01",
            "nom": 'Xpert Carba-R Version 2',
            "abbr": '',
            "famille": 23,
            "cote_unite": '',
            "cote_valeur": 0,
            "commentaire": '',
            "sample_code": "Selles",
            "ana_loinc": "85502-3",
        },
        {
            "key": "GX02",
            "code": "GX02",
            "nom": 'Xpert HBV Viral Load Version 1',
            "abbr": '',
            "famille": 23,
            "cote_unite": '',
            "cote_valeur": 0,
            "commentaire": '',
            "sample_code": "Sang",
            "ana_loinc": "95147-5",
        },
        {
            "key": "GX03",
            "code": "GX03",
            "nom": 'Xpert HIV-1 Qual XC DBS Version 1',
            "abbr": '',
            "famille": 23,
            "cote_unite": '',
            "cote_valeur": 0,
            "commentaire": '',
            "sample_code": "Sang",
            "ana_loinc": "83101-6",
        },
        {
            "key": "GX04",
            "code": "GX04",
            "nom": 'Xpert HIV-1 Qual XC WB Version 1',
            "abbr": '',
            "famille": 23,
            "cote_unite": '',
            "cote_valeur": 0,
            "commentaire": '',
            "sample_code": "Sang",
            "ana_loinc": "83101-6",
        },
        {
            "key": "GX05",
            "code": "GX05",
            "nom": 'Xpert HIV-1 Viral Load XC Version 3',
            "abbr": '',
            "famille": 23,
            "cote_unite": '',
            "cote_valeur": 0,
            "commentaire": '',
            "sample_code": "Sang",
            "ana_loinc": "81246-1",
        },
        {
            "key": "GX06",
            "code": "GX06",
            "nom": 'Xpert MTB-RIF Ultra Version 4',
            "abbr": '',
            "famille": 23,
            "cote_unite": '',
            "cote_valeur": 0,
            "commentaire": '',
            "sample_code": "LBA",
            "ana_loinc": "89371-9",
        },
        {
            "key": "GX07",
            "code": "GX07",
            "nom": 'Xpert Xpress SARS-CoV-2 Version 2',
            "abbr": '',
            "famille": 23,
            "cote_unite": '',
            "cote_valeur": 0,
            "commentaire": '',
            "sample_code": "nasophar",
            "ana_loinc": "94531-1",
        },
        {
            "key": "GX08",
            "code": "GX08",
            "nom": 'Xpert_Carba-R Version 1',
            "abbr": '',
            "famille": 23,
            "cote_unite": '',
            "cote_valeur": 0,
            "commentaire": '',
            "sample_code": "Selles",
            "ana_loinc": "85502-3",
        },
        {
            "key": "GX09",
            "code": "GX09",
            "nom": 'Xpert_HIV-1 Qual Version 2',
            "abbr": '',
            "famille": 23,
            "cote_unite": '',
            "cote_valeur": 0,
            "commentaire": '',
            "sample_code": "Sang",
            "ana_loinc": "83101-6",
        },
        {
            "key": "GX10",
            "code": "GX10",
            "nom": 'Xpert_HIV-1 Viral Load Version 1',
            "abbr": '',
            "famille": 23,
            "cote_unite": '',
            "cote_valeur": 0,
            "commentaire": '',
            "sample_code": "Sang",
            "ana_loinc": "81246-1",
        },
    ]

    ana_ids = {}

    for a in analyses_def:
        row = conn.execute(
            text(
                """
                SELECT id_data
                FROM sigl_05_data
                WHERE id_owner = 1 AND code = :code
                LIMIT 1
                """
            ),
            {"code": a["code"]},
        ).fetchone()

        if row:
            ana_ids[a["key"]] = row.id_data
            continue

        sample_id = get_type_prel_id_by_code(a["sample_code"])

        res = conn.execute(
            text(
                """
                INSERT INTO sigl_05_data
                (id_owner,
                 code,
                 nom,
                 abbr,
                 famille,
                 cote_unite,
                 cote_valeur,
                 commentaire,
                 produit_biologique,
                 type_prel,
                 type_analyse,
                 actif,
                 ana_whonet,
                 ana_ast,
                 ana_loinc,
                 ana_lite)
                VALUES
                (
                 1,
                 :code,
                 :nom,
                 :abbr,
                 :famille,
                 :cote_unite,
                 :cote_valeur,
                 :commentaire,
                 0,
                 :type_prel,
                 NULL,
                 4,
                 5,
                 'N',
                 :ana_loinc,
                 'N'
                )
                """
            ),
            {
                "code": a["code"],
                "nom": a["nom"],
                "abbr": a["abbr"],
                "famille": a["famille"],
                "cote_unite": a["cote_unite"],
                "cote_valeur": a["cote_valeur"],
                "commentaire": a["commentaire"],
                "type_prel": sample_id,
                "ana_loinc": a["ana_loinc"],
            },
        )

        new_id = res.lastrowid
        ana_ids[a["key"]] = new_id

    # Create links sigl_05_07_data
    links_def = [
        ("GX01", "IMP1",       1,   1),
        ("GX01", "KPC",       20,   2),
        ("GX01", "NDM",       30,   3),
        ("GX01", "OXA48",     40,   4),
        ("GX01", "VIM",       50,   5),

        ("GX02", "HBV_VL",     1,   1),

        ("GX03", "HIV1",       1,   1),
        ("GX03", "QC",        20,   2),

        ("GX04", "HIV1",       1,   1),
        ("GX04", "QC",        20,   2),

        ("GX05", "HIV1_VL_XC", 1,   1),

        ("GX06", "MTB",        1,   1),
        ("GX06", "MTB_TRACE", 20,   2),
        ("GX06", "RIF_RES",   30,   3),

        ("GX07", "SC2",        1,   1),

        ("GX08", "IMP",        1,   1),
        ("GX08", "KPC",       20,   2),
        ("GX08", "NDM",       30,   3),
        ("GX08", "OXA48",     40,   4),
        ("GX08", "VIM",       50,   5),

        ("GX09", "HIV1",       1,   1),
        ("GX09", "QC",        20,   2),

        ("GX10", "HIV1_VL",    1,   1),
    ]

    for ana_key, var_key, position, num_var in links_def:
        id_refanalyse = ana_ids.get(ana_key)
        id_refvariable = var_ids.get(var_key)

        if not id_refanalyse or not id_refvariable:
            continue

        existing = conn.execute(
            text(
                """
                SELECT id_data
                FROM sigl_05_07_data
                WHERE id_owner = 1
                  AND id_refanalyse = :id_refanalyse
                  AND id_refvariable = :id_refvariable
                LIMIT 1
                """
            ),
            {
                "id_refanalyse": id_refanalyse,
                "id_refvariable": id_refvariable,
            },
        ).fetchone()

        if existing:
            continue

        conn.execute(
            text(
                """
                INSERT INTO sigl_05_07_data
                (id_owner,
                 id_refanalyse,
                 id_refvariable,
                 position,
                 num_var,
                 obligatoire,
                 var_whonet,
                 var_qrcode)
                VALUES
                (
                 1,
                 :id_refanalyse,
                 :id_refvariable,
                 :position,
                 :num_var,
                 4,
                 5,
                 'N'
                )
                """
            ),
            {
                "id_refanalyse": id_refanalyse,
                "id_refvariable": id_refvariable,
                "position": position,
                "num_var": num_var,
            },
        )

    print(str(datetime.today()) + " : END of migration v3_6_6_genexpert_analyzes revision=85720bfb7d7e")


def downgrade():
    """
    No-op by design.

    This migration is intentionally irreversible per the organization's
    forward-only policy. It includes destructive operations and/or renames
    that cannot be safely undone. To roll back, restore a verified backup
    taken before revision 85720bfb7d7e.
    """
    print("downgrade skipped: irreversible migration 85720bfb7d7e (forward-only policy)")
