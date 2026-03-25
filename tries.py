#===============================================================================================
#run apps
#===============================================================================================
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
        


#==================================================================================================
#collapsible columns
#==================================================================================================
#resizable columns for applications & helps
selector_frame = tk.Frame(window)
selector_frame.pack(pady=10, fill="x")

left_col = tk.Frame(selector_frame)
left_col.pack(side="left", anchor="n", padx=20)

right_col = tk.Frame(selector_frame)
right_col.pack(side="right", anchor="n", padx=20)

apps_btn = tk.Button(left_col, text="Applications ▼",
                     command=lambda: toggle(apps_list, tk.W))
apps_btn.pack(anchor=tk.W)
app_vars = {}

apps_list = tk.Frame(left_col)
apps_list.pack(anchor=tk.W)

for app in apps:
    var = tk.BooleanVar(value=True)
    app_vars[app] = var
    tk.Checkbutton(apps_list, text=app, variable=var).pack(anchor=tk.W)

help_btn = tk.Button(right_col, text="Help ▼",
                     command=lambda: toggle(help_list, tk.E))
help_btn.pack(anchor=tk.E)

help_list = tk.Frame(right_col)
help_list.pack(anchor=tk.E)

help_vars = {}

for help_file in help_files:
    var = tk.BooleanVar(value=True)
    help_vars[help_file] = var
    tk.Checkbutton(help_list, text=help_file, variable=var).pack(anchor=tk.E)

def toggle(frame, anchor):
    if frame.winfo_viewable():
        frame.pack_forget()
    else:
        frame.pack(anchor=anchor)
