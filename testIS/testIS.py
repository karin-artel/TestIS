import datetime
import os
import sys
from pathlib import Path

import win32api
import win32con

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app_config import apps, config
from testIS.ui import TestISUI


def create_log_files():
    try:
        if not os.path.exists(config["dir_logs"]):
            os.makedirs(config["dir_logs"])
    except Exception as e:
        print(f"Error creating directory {config['dir_logs']}: {e}")
        return False

    try:
        all_checks = open(os.path.join(config["dir_logs"], "all_checks.log"), "w")
        failures = open(os.path.join(config["dir_logs"], "failures.log"), "w")
        return all_checks, failures
    except Exception as e:
        print(f"Error creating log files: {e}")
        return None


def check_apps(all_checks, failures):
    for app in apps:
        app_path = os.path.join(config["dir_IS"], app)

        if not os.path.exists(app_path):
            log_check(app, "application exists", False, "file not found", all_checks, failures)
            continue

        app_version = get_exe_version(app_path)
        if not app_version:
            log_check(app, "version", False, "error reading version", all_checks, failures)
            continue

        version_ok = app_version.startswith(config["tb_version"])
        icon_ok = has_icon(app_path)
        compilation_date = get_compilation_date(app_path)
        compile_date_ok = compilation_date == config["install_date"]

        log_check(
            app,
            "version",
            version_ok,
            f"{app_version} (expected {config['tb_version']}.x)",
            all_checks,
            failures,
        )
        icon_details = "icon resource found" if icon_ok else "icon resource not found"
        log_check(app, "icon", icon_ok, icon_details, all_checks, failures)
        log_check(
            app,
            "compilation date",
            compile_date_ok,
            f"{compilation_date} (expected {config['install_date']})",
            all_checks,
            failures,
        )

    print()
    all_checks.write("\n")
    all_checks.flush()
    failures.flush()


def get_exe_version(app_path):
    try:
        info = win32api.GetFileVersionInfo(app_path, "\\")
        ms = info["FileVersionMS"]
        ls = info["FileVersionLS"]
        return f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
    except Exception:
        return None


def log(msg, all_checks, failures=None, is_failure=False):
    print(msg)
    all_checks.write(msg + "\n")
    if is_failure and failures:
        failures.write(msg + "\n")


def log_check(item, check_name, passed, details, all_checks, failures):
    status = "OK" if passed else "FAILED"
    message = f"{item} - {check_name}: {status} - {details}"
    log(message, all_checks, failures, not passed)


def has_icon(exe_path):
    try:
        hmodule = win32api.LoadLibraryEx(
            exe_path,
            0,
            win32con.LOAD_LIBRARY_AS_DATAFILE,
        )
        icons = win32api.EnumResourceNames(hmodule, win32con.RT_GROUP_ICON)
        return len(icons) > 0
    except Exception:
        return False


def get_compilation_date(app_path):
    timestamp = os.path.getmtime(app_path)
    return datetime.date.fromtimestamp(timestamp)


def compare_dirs(dir1, dir2, all_checks, failures):
    files_IS = {
        f: os.path.getsize(os.path.join(dir1, f))
        for f in os.listdir(dir1)
        if os.path.isfile(os.path.join(dir1, f))
    }

    files_compareto = {
        f: os.path.getsize(os.path.join(dir2, f))
        for f in os.listdir(dir2)
        if os.path.isfile(os.path.join(dir2, f))
    }

    mismatches = []

    for file, size in files_IS.items():
        if file not in files_compareto:
            mismatches.append(f"{file} - Missing in comparison directory")
        elif files_compareto[file] != size:
            mismatches.append(
                f"{file} - Size mismatch (IS: {size} bytes, Compare: {files_compareto[file]} bytes)"
            )

    for file in files_compareto:
        if file not in files_IS:
            mismatches.append(f"{file} - Extra file in comparison directory")

    dir_name = os.path.basename(dir1)
    if mismatches:
        header = f"{dir_name} - directory comparison: FAILED"
        print(header)
        all_checks.write(f"{header}\n")
        failures.write(f"{header}\n")

        for mismatch in mismatches:
            message = f"{dir_name} - file comparison: FAILED - {mismatch}"
            print(message)
            all_checks.write(f"{message}\n")
            failures.write(f"{message}\n")
    else:
        log_check(dir_name, "directory comparison", True, "all files match", all_checks, failures)

    print()
    all_checks.write("\n")
    all_checks.flush()
    failures.flush()


def check_dirs(all_checks, failures):
    dir_IS_help = os.path.join(config["dir_IS"], "Help")
    dir_compareto_help = os.path.join(config["dir_compareto"], "Help")
    compare_dirs(dir_IS_help, dir_compareto_help, all_checks, failures)

    dir_IS_toolbox = os.path.join(config["dir_IS"], "ToolboxSystem")
    dir_compareto_toolbox = os.path.join(config["dir_compareto"], "ToolboxSystem")
    compare_dirs(dir_IS_toolbox, dir_compareto_toolbox, all_checks, failures)

    dir_IS_texts = os.path.join(config["dir_IS"], "ToolboxSystem\\Texts\\en-Us")
    dir_compareto_texts = os.path.join(config["dir_compareto"], "ToolboxSystem\\Texts\\en-Us")
    compare_dirs(dir_IS_texts, dir_compareto_texts, all_checks, failures)

    dir_IS_sql = os.path.join(config["dir_IS"], "CreateDBSql")
    dir_compareto_sql = os.path.join(config["dir_compareto"], "CreateDBSql")
    compare_dirs(dir_IS_sql, dir_compareto_sql, all_checks, failures)

    dir_IS_data = os.path.join(config["dir_IS"], "ToolboxSystem\\Data")
    dir_compareto_data = os.path.join(config["dir_compareto"], "ToolboxSystem\\Data")
    compare_dirs(dir_IS_data, dir_compareto_data, all_checks, failures)


def main(ui):
    log_files = create_log_files()
    if not log_files:
        print("Failed to create log files")
        return

    all_checks, failures = log_files

    try:
        ui.create_output_window()
        check_apps(all_checks, failures)
        check_dirs(all_checks, failures)
    finally:
        all_checks.close()
        failures.close()

    ui.update_log_buttons()
    print("\nAll checks complete!")


def start_app():
    app_ui = TestISUI(config, lambda: main(app_ui))
    app_ui.start()



if __name__ == "__main__":
    start_app()
