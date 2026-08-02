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
        f"UID={config['sql_login']};"
        f"PWD={config['sql_password']};"
        "TrustServerCertificate=yes;"
    )

    database_sql = config["database"].replace("]", "]]")
    owner_sql = config["login_name"].replace("'", "''")
    backup_file_sql = backup_file.replace("'", "''")

    data_file = os.path.join(
        config["database_data_path"],
        f"{config['database']}.mdf",
    )
    log_file = os.path.join(
        config["database_log_path"],
        f"{config['database']}_log.ldf",
    )

    data_file_sql = data_file.replace("'", "''")
    log_file_sql = log_file.replace("'", "''")

    print(f"Connecting to SQL Server '{config['server']}'...")
    connection = pyodbc.connect(connection_string, autocommit=True, timeout=300)
    cursor = connection.cursor()
    print("Connected to SQL Server.")

    try:
        cursor.execute(
            "SELECT state_desc FROM sys.databases WHERE name = ?",
            config["database"],
        )
        row = cursor.fetchone()

        if row:
            state_desc = row[0]
            print(
                f"Database '{config['database']}' already exists "
                f"with state '{state_desc}'."
            )

            if state_desc == "RESTORING":
                print(f"Dropping database '{config['database']}'...")
                cursor.execute(f"DROP DATABASE [{database_sql}]")
            else:
                print(f"Setting database '{config['database']}' to single-user mode...")
                cursor.execute(f"""
                    ALTER DATABASE [{database_sql}]
                    SET SINGLE_USER
                    WITH ROLLBACK IMMEDIATE
                """)

                print(f"Dropping database '{config['database']}'...")
                cursor.execute(f"DROP DATABASE [{database_sql}]")

        print(
            f"Restoring database '{config['database']}' "
            f"from '{backup_file}'..."
        )
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

        print(f"Database '{config['database']}' restored successfully.")
        print(
            f"Changing database owner to '{config['login_name']}'..."
        )
        cursor.execute(f"""
            USE [{database_sql}]
            EXEC sp_changedbowner N'{owner_sql}', true
        """)

        while cursor.nextset():
            pass

        print(
            f"Database owner changed to '{config['login_name']}'."
        )

    finally:
        connection.close()
        print("SQL Server connection closed.")
