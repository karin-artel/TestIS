import datetime
import json
import sys
import tkinter as tk
from tkinter import messagebox
from pathlib import Path


def get_config_file():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().with_name("app_config.json")

    return Path(__file__).with_name("app_config.json")


CONFIG_FILE = get_config_file()

config = {}
apps = []


def show_error_window(title, message):
    try:
        error_window = tk.Tk()
        error_window.withdraw()
        error_window.attributes("-topmost", True)
        messagebox.showerror(title, message, parent=error_window)
        error_window.destroy()
    except tk.TclError:
        print(message)


def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            raw_config = json.load(file)
    except FileNotFoundError:
        message = f"Configuration file not found:\n{CONFIG_FILE}"
        show_error_window("Configuration error", message)
        raise
    except json.JSONDecodeError as error:
        message = (
            "The app_config.json file is invalid.\n\n"
            f"File: {CONFIG_FILE}\n"
            f"Line: {error.lineno}, column: {error.colno}\n"
            f"Details: {error.msg}"
        )
        show_error_window("Invalid configuration", message)
        raise
    except Exception as error:
        message = (
            "An error occurred while loading app_config.json.\n\n"
            f"File: {CONFIG_FILE}\n"
            f"Error: {type(error).__name__}: {error}"
        )
        show_error_window("Configuration error", message)
        raise

    general_config = raw_config.get("general", {})
    testIS_config = raw_config.get("testIS", {})
    test_license_config = raw_config.get("test_license", {})

    loaded_config = {}
    loaded_config.update(general_config)
    loaded_config.update(testIS_config)
    loaded_config.update(test_license_config)

    if isinstance(loaded_config.get("install_date"), str):
        loaded_config["install_date"] = datetime.datetime.strptime(
            loaded_config["install_date"],
            "%Y-%m-%d",
        ).date()

    loaded_apps = testIS_config.get("apps", [])
    return loaded_config, loaded_apps


def reload_config():
    loaded_config, loaded_apps = load_config()

    config.clear()
    config.update(loaded_config)

    apps.clear()
    apps.extend(loaded_apps)

    return config, apps


reload_config()
