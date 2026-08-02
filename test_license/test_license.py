import os
import re
import subprocess
import sys
import time
import traceback
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app_config import config, reload_config, show_error_window
from sql.restore_database import restore_database
from test_license.app_login import close_login_popup_if_present, login_to_app
from test_license.ui import LicenseTestUI



def modify_configs():
    modify_toolboxuser_config()
    modify_databases_config()    



def modify_databases_config():
    source_file = os.path.join(config["dir_IS"], "ToolboxSystem", "Data", "Databases.config")
    dest_file = os.path.join(config["dir_IS"], "ToolboxSystem", "Databases.config")

    try:
        print(f"Reading Databases.config from '{source_file}'...")
        with open(source_file, 'r', encoding="latin-1") as file:
            content = file.read()

        content = content.replace("ExampleDB", f"{config['database']}")
        content = content.replace("ExampleSqlSRV", f"{config['server']}")

        with open(dest_file, 'w', encoding="latin-1") as file:
            file.write(content)

        os.remove(source_file)
        print(f"Updated Databases.config and moved it to '{dest_file}'.")

    except FileNotFoundError:
        print(f"Databases.config not found at '{source_file}' - skipping")
    except Exception as e:
        print(f"Error modifying Databases.config: {e}")



def modify_toolboxuser_config():
    source_file = os.path.join(config["dir_IS"], "ToolboxSystem", "Data", "_ToolBoxUser.config")
    dest_file = os.path.join(config["dir_IS"], "_ToolBoxUser.config")

    try:
        if os.path.exists(source_file):
            config_file = source_file
        elif os.path.exists(dest_file):
            config_file = dest_file
            print(
                f"Source _ToolBoxUser.config is missing; "
                f"repairing existing file '{dest_file}'..."
            )
        else:
            raise FileNotFoundError(source_file)

        print(f"Reading _ToolBoxUser.config from '{config_file}'...")
        with open(config_file, 'r', encoding="latin-1") as file:
            content = file.read()

        configured_install_dir = config["dir_IS"].rstrip("\\/")
        content, replacements = re.subn(
            r"[a-zA-Z]:\\Toolbox AP",
            configured_install_dir,
            content,
        )

        if replacements == 0:
            print("No old Toolbox AP installation path was found in _ToolBoxUser.config.")

        with open(dest_file, 'w', encoding="latin-1") as file:
            file.write(content)

        if config_file == source_file:
            os.remove(source_file)
        print(f"Updated _ToolBoxUser.config and moved it to '{dest_file}'.")
    except FileNotFoundError:
        print(f"_ToolBoxUser.config not found at '{source_file}' - skipping")
    except Exception as e:
        print(f"Error modifying _ToolBoxUser.config: {e}")



def run_app(app_name):
    app_path = os.path.join(config["dir_IS"], app_name)

    if not os.path.exists(app_path):
        raise FileNotFoundError(
            f"Application '{app_name}' not found at '{app_path}'"
        )

    try:
        print(f"Starting '{app_path}'...")
        process = subprocess.Popen([app_path])
        print(f"Started '{app_name}' with process id {process.pid}.")
        return process
    except Exception as e:
        raise RuntimeError(
            f"Unexpected error running application '{app_name}': {e}"
        ) from e


def close_app(process):
    if process.poll() is not None:
        print(f"Application process {process.pid} has already exited.")
        return

    print(f"Closing application process {process.pid}...")
    process.terminate()

    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)
    print(f"Application process {process.pid} closed.")


def test_backup_login(backup_name):
    print(f"\nTesting backup: {backup_name}")
    print(f"Restoring database '{config['database']}' from backup '{backup_name}'...")
    restore_database(backup_name)
    print(f"Restored database '{config['database']}' from backup '{backup_name}'.")

    process = run_app("Planner.exe")

    try:
        print("Logging in to Planner...")
        login_to_app(process.pid, config)
        print("Login submitted. Waiting for the result...")
        popup_was_shown = close_login_popup_if_present(process.pid)

        if popup_was_shown:
            print(f"{backup_name}: login failed")
        else:
            print(f"{backup_name}: login succeeded")

        time.sleep(1)
    finally:
        close_app(process)


def main(ui):
    try:
        print("Starting license test.")
        print("Loading configuration...")
        reload_config()
        print("Configuration loaded.")

        print("Modifying application configuration files...")
        modify_databases_config()
        modify_toolboxuser_config()
        print("Application configuration step finished.")

        for backup_name in config["backups"]:
            test_backup_login(backup_name)

        print("All license tests complete.")
    except Exception as error:
        error_details = traceback.format_exc()
        print("\nThe license test failed:")
        print(error_details)
        show_error_window(
            "License test error",
            f"The license test could not continue.\n\n"
            f"Error: {type(error).__name__}: {error}",
        )
    finally:
        ui.set_finished()


def start_app():
    app_ui = LicenseTestUI(lambda: main(app_ui))
    app_ui.start()



if __name__ == "__main__":
    start_app()
