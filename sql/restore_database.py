import os
import sys
from pathlib import Path

import pyodbc

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app_config import config


def restore_database(backup_name):
    backup_file = os.path.join(config["backup_path"], backup_name)

    driver = "ODBC Driver 17 for SQL Server"
    connection_string = (
        f"DRIVER={{{driver}}};"
        f"SERVER={config['server']};"
        "DATABASE=master;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

    database_sql = config["database"].replace("]", "]]")
    owner_sql = config["login_name"].replace("'", "''")
    backup_file_sql = backup_file.replace("'", "''")

    data_file = rf"D:\MSSQL\Data\{config['database']}.mdf"
    log_file = rf"D:\MSSQL\Data\{config['database']}_log.ldf"

    data_file_sql = data_file.replace("'", "''")
    log_file_sql = log_file.replace("'", "''")

    connection = pyodbc.connect(connection_string, autocommit=True, timeout=300)
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT state_desc FROM sys.databases WHERE name = ?",
            config["database"],
        )
        row = cursor.fetchone()

        if row:
            state_desc = row[0]

            if state_desc == "RESTORING":
                cursor.execute(f"DROP DATABASE [{database_sql}]")
            else:
                cursor.execute(f"""
                    ALTER DATABASE [{database_sql}]
                    SET SINGLE_USER
                    WITH ROLLBACK IMMEDIATE
                """)

                cursor.execute(f"DROP DATABASE [{database_sql}]")

        cursor.execute(f"""
            RESTORE DATABASE [{database_sql}]
            FROM DISK = N'{backup_file_sql}'
            WITH
                MOVE N'Example' TO N'{data_file_sql}',
                MOVE N'Example_log' TO N'{log_file_sql}',
                REPLACE,
                RECOVERY,
                STATS = 10
        """)

        while cursor.nextset():
            pass

        cursor.execute(f"""
            USE [{database_sql}]
            EXEC sp_changedbowner N'{owner_sql}', true
        """)

        while cursor.nextset():
            pass

    finally:
        connection.close()
