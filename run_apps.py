#alter _ToolBoxUser.config", move it to the root of Toolbox AP
from asyncio import subprocess
import os
from time import time


source_file = "d:\\Toolbox AP\\ToolboxSystem\\Data\\_ToolBoxUser.config"
dest_file = "d:\\Toolbox AP\\_ToolBoxUser.config"

try:
    with open(source_file, 'r') as file:
        content = file.read()

    content = content.replace("c:\\", "d:\\")

    with open(dest_file, 'w') as file:
        file.write(content)

    os.remove(source_file)
except FileNotFoundError:
     print("_ToolBoxUser.config not found - skipping (already modified or doesn't exist)")
except Exception as e:
    print(f"Error modifying _ToolBoxUser.config: {e}")

#add licensed_db to Databases.config, move it to the ToolboxSystem folder
source_file = "d:\\Toolbox AP\\ToolboxSystem\\Data\\Databases.config"
dest_file = "d:\\Toolbox AP\\ToolboxSystem\\Databases.config"

try:
    with open(source_file, 'r') as file:
        content = file.read()

    content = content.replace("ExampleDB", f"{licensed_db}")
    content = content.replace("ExampleSqlSRV", f"{server}")

    with open(dest_file, 'w') as file:
        file.write(content)

    os.remove(source_file)
except FileNotFoundError:
     print("Databases.config not found - skipping (already modified or doesn't exist)")
except Exception as e:
    print(f"Error modifying Databases.config: {e}")


#run & stop all the apps. If any of them crashes, stop the script execution and report the error
for app in apps:
        app_path = os.path.join(dir_IS, app)
        subprocess.Popen(app_path)
        time.sleep(3)

        print(f"Stopping {app}...")
        app_name = app.replace(".exe", "")
        os.system(f"taskkill /IM {app} /F")
        