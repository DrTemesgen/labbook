"""v3_6_9_new_analysis_for_sysmex

Revision ID: eb7fca49548a
Revises: 7dcf36bd5c39
Create Date: 2026-01-14 09:00:44.999887

"""
from alembic import op
from sqlalchemy import text
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'eb7fca49548a'
down_revision = '7dcf36bd5c39'
branch_labels = None
depends_on = None


def upgrade():
    print("--- " + str(datetime.today()) + "---")
    print("START of migration v3_6_9_new_analysis_for_sysmex revision=eb7fca49548a")

    conn = op.get_bind()
    OWNER_ID = 1

    # COPY alembic io, erase file only if more recent
    try:
        from distutils.dir_util import copy_tree

        fromDirectory = "alembic/io"
        toDirectory = "/storage/io"

        copy_tree(fromDirectory, toDirectory, update=1)
    except Exception as err:
        print("ERROR copy alembic io,\n\terr=" + str(err))

    # ADD schedule kind 'H' (hourly)
    try:
        conn.execute(text(
            "ALTER TABLE automation_job "
            "MODIFY ajb_schedule_kind enum('H','D','W','M','B','T','Q','S','A') NOT NULL"
        ))
    except Exception as err:
        print("WARN alter automation_job.ajb_schedule_kind err=" + str(err))

    # ADD type kind 'system'
    try:
        conn.execute(text(
            "ALTER TABLE automation_job "
            "MODIFY ajb_type enum('dhis2','activity','billing','system') NOT NULL"
        ))
    except Exception as err:
        print("WARN alter automation_job.ajb_schedule_kind err=" + str(err))

    # CREATE default automation job for NTP status (hourly)
    try:
        row = conn.execute(
            text("SELECT ajb_ser FROM automation_job WHERE ajb_label = :label LIMIT 1"),
            {"label": "System NTP status check"},
        ).fetchone()

        if not row:
            conn.execute(
                text(
                    "INSERT INTO automation_job ("
                    "ajb_type, ajb_label, ajb_is_active, ajb_schedule_kind, ajb_schedule_time, "
                    "ajb_fire_on, ajb_next_run_at, ajb_last_status, ajb_params"
                    ") VALUES ("
                    "'system', :label, 'Y', 'H', '00:00:00', 'period_end', NOW(), 'never', "
                    "JSON_OBJECT("
                    "'type','ssh',"
                    "'host','env:LABBOOK_DB_HOST',"
                    "'user','sigl',"
                    "'command','/storage/io/ntp_status.sh',"
                    "'timeout',30,"
                    "'audit','Y'"
                    ")"
                    ")"
                ),
                {"label": "System NTP status check"},
            )
    except Exception as err:
        print("ERROR insert automation job NTP err=" + str(err))

    # Keep existing dictionary inserts
    try:
        conn.execute(text(
            'insert into sigl_dico_data (id_owner, dico_name, label, short_label, position, code) '
            'values (1, "absent", "Absence", "absence", 30, "absence")'
        ))
    except Exception as err:
        print("ERROR insert the feminine form of absence,\n\terr=" + str(err))

    try:
        conn.execute(text(
            'insert into sigl_dico_data (id_owner, dico_name, label, short_label, position, code) '
            'values (1, "absent", "Présence", "presence", 40, "presence")'
        ))
    except Exception as err:
        print("ERROR insert the feminine form of présent,\n\terr=" + str(err))

    # Variables definition (sigl_07_data)
    vars_def = [
        {"code_var": "RBC",    "libelle": "Hématies",                   "unite": 241, "normal_min": "4.0",   "normal_max": "5.7",   "type_resultat": 228, "accuracy": 1},
        {"code_var": "837",    "libelle": "Numération globulaire",      "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 265, "accuracy": 0},
        {"code_var": "HGB",    "libelle": "Hémoglobine",                "unite": 243, "normal_min": "12.0",  "normal_max": "17.0",  "type_resultat": 228, "accuracy": 1},
        {"code_var": "HCT",    "libelle": "Hématocrite",                "unite": 239, "normal_min": "36.0",  "normal_max": "52.0",  "type_resultat": 228, "accuracy": 1},
        {"code_var": "MCV",    "libelle": "VGM",                        "unite": 244, "normal_min": "80.0",  "normal_max": "100.0", "type_resultat": 228, "accuracy": 1},
        {"code_var": "MCH",    "libelle": "TCMH",                       "unite": 245, "normal_min": "26.0",  "normal_max": "34.0",  "type_resultat": 228, "accuracy": 1},
        {"code_var": "MCHC",   "libelle": "CCMH",                       "unite": 246, "normal_min": "31.0",  "normal_max": "37.0",  "type_resultat": 228, "accuracy": 1},
        {"code_var": "WBC",    "libelle": "Leucocytes",                 "unite": 242, "normal_min": "4.0",   "normal_max": "10.0",  "type_resultat": 228, "accuracy": 1},
        {"code_var": "PLT",    "libelle": "Plaquettes",                 "unite": 240, "normal_min": "150.0", "normal_max": "400.0", "type_resultat": 228, "accuracy": 0},
        {"code_var": "845",    "libelle": "P.L.C.R",                    "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "MPV",    "libelle": "VPM",                        "unite": 247, "normal_min": "7.0",   "normal_max": "11.0",  "type_resultat": 228, "accuracy": 1},
        {"code_var": "PCT",    "libelle": "Thrombocrite",               "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "PDW",    "libelle": "IDP",                        "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "RDW-SD", "libelle": "IDR-SD",                     "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "RDW-CV", "libelle": "IDR-CV",                     "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "NEUT#",  "libelle": "Neutrophiles#",              "unite": 242, "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "LYMPH#", "libelle": "Lymphocytes#",               "unite": 242, "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "MONO#",  "libelle": "Monocytes#",                 "unite": 242, "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "EO#",    "libelle": "Eosinophiles#",              "unite": 242, "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "BASO#",  "libelle": "Basophiles#",                "unite": 242, "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "NEUT%",  "libelle": "Neutrophiles%",              "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "LYMPH%", "libelle": "Lymphocytes%",               "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "MONO%",  "libelle": "Monocytes%",                 "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "EO%",    "libelle": "Eosinophiles%",              "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "BASO%",  "libelle": "Basophiles%",                "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "IG#",    "libelle": "Granulocytes immatures#",    "unite": 242, "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "IG%",    "libelle": "Granulocytes immatures%",    "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "846",    "libelle": "NRBC#",                      "unite": 242, "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "NRBC%",  "libelle": "NRBC%",                      "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "849",    "libelle": "RET#",                       "unite": 242, "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "RET%",   "libelle": "RET%",                       "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "852",    "libelle": "IRF",                        "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "LFR",    "libelle": "LFR",                        "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "MFR",    "libelle": "MFR",                        "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "HFR",    "libelle": "HFR",                        "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "863",    "libelle": "Delta-He",                   "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "864",    "libelle": "RET-He",                     "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "868",    "libelle": "RBC-He",                     "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "857",    "libelle": "Hypo-He",                    "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "858",    "libelle": "Hyper-He",                   "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "881",    "libelle": "Hypo% (HGB<17)",             "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "882",    "libelle": "Hyper% (HGB>41)",            "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "886",    "libelle": "MicroR",                     "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "887",    "libelle": "MacroR",                     "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "898",    "libelle": "Immature Platelet Fraction", "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
        {"code_var": "910",    "libelle": "Immature Platelet Count",    "unite": 0,   "normal_min": "",      "normal_max": "",      "type_resultat": 228, "accuracy": 1},
    ]

    var_ids = {}

    for v in vars_def:
        res = conn.execute(
            text(
                """
                INSERT INTO sigl_07_data (id_owner, libelle, description, unite, normal_min, normal_max,
                                          commentaire, type_resultat, unite2, formule_unite2, formule,
                                          accuracy, precision2, code_var, var_highlight,
                                          var_show_minmax, var_in_report)
                VALUES (:id_owner, :libelle, '', :unite, :normal_min, :normal_max,
                        '', :type_resultat, 0, '', '',
                        :accuracy, 0, :code_var, 'N', 'N', 'Y')
                """
            ),
            {
                "id_owner": OWNER_ID,
                "libelle": v["libelle"],
                "unite": v["unite"],
                "normal_min": v["normal_min"],
                "normal_max": v["normal_max"],
                "type_resultat": v["type_resultat"],
                "accuracy": v["accuracy"],
                "code_var": v["code_var"],
            },
        )

        var_ids[v["code_var"]] = res.lastrowid

    # Create analysis (sigl_05_data)
    ana_code = "NFS_XN3"

    row = conn.execute(
        text(
            """
            SELECT id_data
            FROM sigl_05_data
            WHERE id_owner = :id_owner AND code = :code
            LIMIT 1
            """
        ),
        {"id_owner": OWNER_ID, "code": ana_code},
    ).fetchone()

    if row:
        ana_id = row.id_data
    else:
        res = conn.execute(
            text(
                """
                INSERT INTO sigl_05_data (id_owner, code, nom, abbr, famille, cote_unite, cote_valeur,
                                          commentaire, produit_biologique, type_prel, type_analyse,
                                          actif, ana_whonet, ana_ast, ana_loinc, ana_lite)
                VALUES (:id_owner, :code, :nom, :abbr, :famille, :cote_unite, :cote_valeur,
                        :commentaire, :produit_biologique, :type_prel, :type_analyse,
                        4, 5, 'N', :ana_loinc, 'N')
                """
            ),
            {
                "id_owner": OWNER_ID,
                "code": "NFS_XN3",
                "nom": "NFS - Automate",
                "abbr": "NFS-Auto",
                "famille": 1001,
                "cote_unite": "B",
                "cote_valeur": 0,
                "commentaire": "Automate Sysmex XN-350",
                "produit_biologique": 0,
                "type_prel": 138,
                "type_analyse": 170,
                "ana_loinc": "57022-6",
            },
        )
        ana_id = res.lastrowid

    # Links (sigl_05_07_data) num_var = 1..46
    links_def = [
        ("837",     10,  1),
        ("RBC",     20,  2),
        ("HGB",     30,  3),
        ("HCT",     40,  4),
        ("MCV",     50,  5),
        ("MCH",     60,  6),
        ("MCHC",    70,  7),
        ("WBC",     80,  8),
        ("PLT",     90,  9),
        ("845",    100, 10),
        ("MPV",    110, 11),
        ("PCT",    120, 12),
        ("PDW",    130, 13),
        ("RDW-SD",  140, 14),
        ("RDW-CV",  150, 15),
        ("NEUT#",   160, 16),
        ("LYMPH#",  170, 17),
        ("MONO#",   180, 18),
        ("EO#",     190, 19),
        ("BASO#",   200, 20),
        ("NEUT%",   210, 21),
        ("LYMPH%",  220, 22),
        ("MONO%",   230, 23),
        ("EO%",     240, 24),
        ("BASO%",   250, 25),
        ("IG#",     260, 26),
        ("IG%",     270, 27),
        ("846",     280, 28),
        ("NRBC%",   290, 29),
        ("849",     300, 30),
        ("RET%",    310, 31),
        ("852",     320, 32),
        ("LFR",     330, 33),
        ("MFR",     340, 34),
        ("HFR",     350, 35),
        ("863",     360, 36),
        ("864",     370, 37),
        ("868",     380, 38),
        ("857",     390, 39),
        ("858",     400, 40),
        ("881",     410, 41),
        ("882",     420, 42),
        ("886",     430, 43),
        ("887",     440, 44),
        ("898",     450, 45),
        ("910",     460, 46),
    ]

    for code_var, position, num_var in links_def:
        id_refvariable = var_ids.get(code_var)
        if not id_refvariable:
            continue

        existing = conn.execute(
            text(
                """
                SELECT id_data
                FROM sigl_05_07_data
                WHERE id_owner = :id_owner
                  AND id_refanalyse = :id_refanalyse
                  AND id_refvariable = :id_refvariable
                LIMIT 1
                """
            ),
            {
                "id_owner": OWNER_ID,
                "id_refanalyse": ana_id,
                "id_refvariable": id_refvariable,
            },
        ).fetchone()

        if existing:
            continue

        conn.execute(
            text(
                """
                INSERT INTO sigl_05_07_data (id_owner, id_refanalyse, id_refvariable,
                                            position, num_var, obligatoire,
                                            var_whonet, var_qrcode)
                VALUES (:id_owner, :id_refanalyse, :id_refvariable,
                        :position, :num_var, 4, 5, 'N')
                """
            ),
            {
                "id_owner": OWNER_ID,
                "id_refanalyse": ana_id,
                "id_refvariable": id_refvariable,
                "position": position,
                "num_var": num_var,
            },
        )

    print(str(datetime.today()) + " : END of migration v3_6_9_new_analysis_for_sysmex revision=eb7fca49548a")


def downgrade():
    """
    No-op by design.

    This migration is intentionally irreversible per the organization's
    forward-only policy. It includes destructive operations and/or renames
    that cannot be safely undone. To roll back, restore a verified backup
    taken before revision eb7fca49548a.
    """
    print("downgrade skipped: irreversible migration eb7fca49548a (forward-only policy)")
