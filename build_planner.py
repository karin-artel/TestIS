import os
import re
import shutil
import subprocess
from pathlib import Path
from app_config import config


CONFIGURATION = "Release"
PLATFORM = "x64"
DEBUG_PROJECT_NAME = "tbDBConnect"

def get_solution_projects(solution_path):
    solution_dir = solution_path.parent
    projects = []

    with open(solution_path, "r", encoding="utf-8-sig") as file:
        for line in file:
            if not line.startswith("Project("):
                continue

            if ".vbproj" not in line and ".csproj" not in line:
                continue

            right_side = line.split(" = ", 1)[1]
            fields = [field.strip().strip('"') for field in right_side.split(",")]

            project_name = fields[0]
            relative_project_path = fields[1]
            project_path = (solution_dir / relative_project_path).resolve()

            projects.append((project_name, project_path))

    return projects


if __name__ == "__main__":
    projects = get_solution_projects(Path(config["app_path"]))
    print(projects)
