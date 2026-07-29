import datetime
import json
from pathlib import Path


CONFIG_FILE = Path(__file__).with_name("app_config.json")

config = {}
apps = []


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        raw_config = json.load(file)

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
