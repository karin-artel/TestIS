import os
import subprocess
import time, datetime   
import tkinter as tk
import win32api

#========================================================================================================================================
#Build a form and input the parameters (directory where IS puts Toolbox, server, database to check with etc.)
#========================================================================================================================================

#directory where the IS puts Toolbox
dir_IS = "d:\\Toolbox AP\\"

#directory with Toolbox installed correctly
dir_compareto = "d:\\Toolbox\\tb_435\\"

server = "LAPTOP-HAYA\SQL2016ST"

licensed_db = "Karin_Lucy_LH"

apps = [ "ActiveUsers.exe", "BAR.exe", "ConfigurationEditor.exe", "DatabaseChecking.exe", "DatabasePurging.exe", 
        "DataScience.exe", "FormulaEditor.exe", "HierarchyManager.exe", "IntegrationBuilder.exe", "LoadData.exe", 
        "LogAnalyzer.exe", "Maintenance.exe", "Planner.exe", "SystemBuilder.exe", "ToolboxDesktop.exe", "UserManagement.exe"]   

tb_version = "4.3.5"

window = tk.Tk()
title = tk.Label(text="Toolbox AP Installation Validation", font=("Arial", 16))
title.pack(pady=10, anchor=tk.W)

dir_IS_frame = tk.Frame(window)
dir_IS_frame.pack(pady=20, anchor=tk.W)
dir_IS_label = tk.Label(dir_IS_frame, width=25, text="Installation directory: ")
dir_IS_label.pack(side = tk.LEFT, padx=10)
dir_IS_entry = tk.Entry(dir_IS_frame, width=30)
dir_IS_entry.pack(side = tk.LEFT, padx=10)
dir_IS_entry.insert(0, dir_IS)

dir_compareto_frame = tk.Frame(window)
dir_compareto_frame.pack(pady=20, anchor=tk.W)
dir_compareto_label = tk.Label(dir_compareto_frame, width=25, text="Comparison directory: ")
dir_compareto_label.pack(side = tk.LEFT, padx=10)
dir_compareto_entry = tk.Entry(dir_compareto_frame, width=30)
dir_compareto_entry.pack(side = tk.LEFT, padx=10)
dir_compareto_entry.insert(0, dir_compareto)

version_frame = tk.Frame(window)
version_frame.pack(pady=10, anchor=tk.CENTER)
version_label = tk.Label(version_frame, width=15, text="Toolbox version: ")
version_label.pack(side = tk.LEFT, padx=10)
version_entry = tk.Entry(version_frame, width=7)
version_entry.pack(side = tk.LEFT, padx=10)
version_entry.insert(0, tb_version)

#checkboxes for applications
chechbox_frame = tk.Frame(window)
chechbox_frame.pack(pady=20)
checkbox_label = tk.Label(chechbox_frame, text="Select applications to check:")
checkbox_label.pack()
app_vars = {}
for app in apps:
    var = tk.BooleanVar(value=True)  # Default checked
    app_vars[app] = var
    checkbox = tk.Checkbutton(chechbox_frame, text=app, variable=var)
    checkbox.pack(anchor=tk.W, padx=20)

frame4 = tk.Frame(window)
frame4.pack(pady=20)

ok_btn = tk.Button(frame4, bg="#4CAF50", fg="white", text="Run Tests")
ok_btn.pack(side=tk.LEFT, padx=10)

window.mainloop()

#========================================================================================================================================
#Check if all files are present (exe, Help, config, etc.)
#========================================================================================================================================
if os.path.exists(os.path.join(dir_IS, "all_checks.log")):
    os.remove(os.path.join(dir_IS, "all_checks.log"))
if os.path.exists(os.path.join(dir_IS, "failures.log")):
    os.remove(os.path.join(dir_IS, "failures.log"))

all_checks = open(os.path.join(dir_IS, "all_checks.log"), "a")  #write everything that was checked + result
failures = open(os.path.join(dir_IS, "failures.log"), "a")   #write only if a check didn't pass

for app in apps:
        app_path = os.path.join(dir_IS, app)
        if not os.path.exists(app_path):
                print(f"{app} not found")
                all_checks.write(f"{app} not found\n")
                failures.write(f"{app} not found\n")
        else:
                try:
                     info = win32api.GetFileVersionInfo(app_path, "\\")
                     app_version = info['FileVersion']
                except Exception as e:
                     print(f"Error getting version for {app}: {e}")
                


'''dir1 is IS, dir2 is compareto. compare dir1 to dir2, report missing files and size mismatches'''
def compare_dirs(dir1, dir2): 
    files_IS = {f: os.path.getsize(os.path.join(dir1, f)) 
            for f in os.listdir(dir1) if os.path.isfile(os.path.join(dir1, f))}

    files_compareto = {f: os.path.getsize(os.path.join(dir2, f)) 
                   for f in os.listdir(dir2) if os.path.isfile(os.path.join(dir2, f))}

    mismatches = []

    for file, size in files_IS.items():
        if file not in files_compareto:
            mismatches.append(f"{file} - Missing in comparison directory")
        elif files_compareto[file] != size:
            mismatches.append(f"{file} - Size mismatch (IS: {size} bytes, Compare: {files_compareto[file]} bytes)")

    for file in files_compareto:
        if file not in files_IS:
            mismatches.append(f"{file} - Extra file in comparison directory")

    # Check for files in dir_compareto_help that don't exist in dir_IS_help
    for file in files_compareto:
        if file not in files_IS:
            mismatches.append(f"{file} - Extra file in comparison directory")

    # Print mismatches
    if mismatches:
        print("Files that do not match:")
        for mismatch in mismatches:
            print(mismatch)
    else:
        print("All files match!")


#compare Helps, configs in Toolbox file, texts, sql, data
dir_IS_help = os.path.join(dir_IS, "Help")
dir_compareto_help = os.path.join(dir_compareto, "Help")
compare_dirs(dir_IS_help, dir_compareto_help)

dir_IS_toolbox = os.path.join(dir_IS, "ToolboxSystem")
dir_compareto_toolbox = os.path.join(dir_compareto, "Toolbox")
compare_dirs(dir_IS_toolbox, dir_compareto_toolbox)

dir_IS_texts = os.path.join(dir_IS, "ToolboxSystem\\Texts\\en-Us")
dir_compareto_texts = os.path.join(dir_compareto, "ToolboxSystem\\Texts\\en-Us")
compare_dirs(dir_IS_texts, dir_compareto_texts)

dir_IS_sql = os.path.join(dir_IS, "CreateDBSql")
dir_compareto_sql = os.path.join(dir_compareto, "CreateDBSql")
compare_dirs(dir_IS_sql, dir_compareto_sql)

dir_IS_data = os.path.join(dir_IS, "ToolboxSystem\\Data")
dir_compareto_data = os.path.join(dir_compareto, "ToolboxSystem\\Data")
compare_dirs(dir_IS_data, dir_compareto_data)



#========================================================================================================================================
#Run the apps, if they crash stop the script execution
#========================================================================================================================================

#alter _ToolBoxUser.config", move it to the root of Toolbox AP
'''source_file = "d:\\Toolbox AP\\ToolboxSystem\\Data\\_ToolBoxUser.config"
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
        '''