import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app_config import config
from sql.restore_database import restore_database
from test_license.app_login import login_to_app



def modify_configs():
    modify_toolboxuser_config()
    modify_databases_config()    



def modify_databases_config():
    source_file = os.path.join(config["dir_IS"], "ToolboxSystem", "Data", "Databases.config")
    dest_file = os.path.join(config["dir_IS"], "ToolboxSystem", "Databases.config")

    try:
        with open(source_file, 'r') as file:
            content = file.read()

        content = content.replace("ExampleDB", f"{config['database']}")
        content = content.replace("ExampleSqlSRV", f"{config['server']}")

        with open(dest_file, 'w') as file:
            file.write(content)

        os.remove(source_file)

    except FileNotFoundError:
        print(f"Databases.config not found at '{source_file}' - skipping")
    except Exception as e:
        print(f"Error modifying Databases.config: {e}")



def modify_toolboxuser_config():
    source_file = os.path.join(config["dir_IS"], "ToolboxSystem", "Data", "_ToolBoxUser.config")
    dest_file = os.path.join(config["dir_IS"], "_ToolBoxUser.config")

    try:
        with open(source_file, 'r') as file:
            content = file.read()

        content = content.replace("c:\\", "d:\\")

        with open(dest_file, 'w') as file:
            file.write(content)

        os.remove(source_file)
    except FileNotFoundError:
        print(f"_ToolBoxUser.config not found at '{source_file}' - skipping")
    except Exception as e:
        print(f"Error modifying _ToolBoxUser.config: {e}")



def run_app(app_name):
    app_path = os.path.join(config["dir_IS"], app_name)

    if not os.path.exists(app_path):
        print(f"Application '{app_name}' not found at '{app_path}'")
        return None

    try:
        return subprocess.Popen([app_path])
    except Exception as e:
        print(f"Unexpected error running application '{app_name}': {e}")
        return None




if __name__ == "__main__":
    restore_database(config["backups"][0])
    modify_databases_config()
    modify_toolboxuser_config()
    process = run_app("Planner.exe")
    if process:
        login_to_app(process.pid, config)
