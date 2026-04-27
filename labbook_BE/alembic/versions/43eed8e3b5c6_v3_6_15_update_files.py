"""v3_6_15_update_files

Revision ID: 43eed8e3b5c6
Revises: 293f26bdbf13
Create Date: 2026-02-09 09:14:27.292477

"""
from alembic import op
from sqlalchemy import text
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '43eed8e3b5c6'
down_revision = '293f26bdbf13'
branch_labels = None
depends_on = None


def upgrade():
    print("--- " + str(datetime.today()) + "---")
    print("START of migration v3_6_15_update_files revision=43eed8e3b5c6")

    conn = op.get_bind()

    # Copy alembic resources to /storage/resource
    # Update file only if source is newer
    try:
        import os
        import shutil

        sourceDirectory = "alembic/resource"
        destinationDirectory = "/storage/resource"

        # Create destination root if missing
        os.makedirs(destinationDirectory, exist_ok=True)

        # Walk through source directory tree
        for sourceRoot, sourceDirectories, sourceFiles in os.walk(sourceDirectory):

            # Keep directory structure
            relativePath = os.path.relpath(sourceRoot, sourceDirectory)
            destinationRoot = destinationDirectory if relativePath == "." else os.path.join(destinationDirectory, relativePath)

            # Create destination directory if missing
            os.makedirs(destinationRoot, exist_ok=True)

            # Copy file if missing or older than source
            for sourceFilename in sourceFiles:
                sourceFilePath = os.path.join(sourceRoot, sourceFilename)
                destinationFilePath = os.path.join(destinationRoot, sourceFilename)

                if not os.path.exists(destinationFilePath):
                    shutil.copy2(sourceFilePath, destinationFilePath)
                else:
                    sourceMtime = os.path.getmtime(sourceFilePath)  # source file modification time
                    destinationMtime = os.path.getmtime(destinationFilePath)

                    if sourceMtime > destinationMtime:
                        shutil.copy2(sourceFilePath, destinationFilePath)

    except Exception as err:
        print("ERROR copy alembic resource,\n\terr=" + str(err))

    try:
        # Insert a compact template for result report (idempotent)
        conn.execute(text("""
            INSERT INTO template_setting (tpl_date, tpl_name, tpl_file, tpl_default, tpl_type)
            SELECT NOW(), 'Modèle résultat compact', 'tpl_result_ana_with_one_result.odt', 'N', 'RES'
            WHERE NOT EXISTS (
                SELECT 1
                FROM template_setting
                WHERE tpl_type = 'RES' and tpl_file = 'tpl_result_ana_with_one_result.odt')
        """))
    except Exception as err:
        print("ERROR insert compact result template for template_setting,\n\terr=" + str(err))

    # ask for update translation in DB
    try:
        # insert a line in init_version
        conn.execute(text("insert into init_version (ini_date, ini_stat) values (NOW(), 'Y')"))
    except Exception as err:
        print("ERROR insert init_version,\n\terr=" + str(err))

    print(str(datetime.today()) + " : END of migration v3_6_15_update_files revision=43eed8e3b5c6")


def downgrade():
    """
    No-op by design.

    This migration is intentionally irreversible per the organization's
    forward-only policy. It includes destructive operations and/or renames
    that cannot be safely undone. To roll back, restore a verified backup
    taken before revision 43eed8e3b5c6.
    """
    print("downgrade skipped: irreversible migration 43eed8e3b5c6 (forward-only policy)")
