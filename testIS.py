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

apps = [ "ActiveUsers.exe", "BAR.exe", "ConfigurationEditor.exe", "DatabaseChecking.exe", 
        "DatabasePurging.exe", "DataScience.exe", "FormulaEditor.exe", "HierarchyManager.exe", 
        "IntegrationBuilder.exe", "LoadData.exe", "LogAnalyzer.exe", "Maintenance.exe", 
        "Planner.exe", "SystemBuilder.exe", "ToolboxDesktop.exe", "UserManagement.exe"]   

help_files = ["AdministrativeGuide", "DatabaseChecking", "HierarchyManager.chm", "InputFileBuilder", 
              "IntegrationBuilder", "LoadData", "MainConcept", "Maintenance", "Planner", "UserManagement"]

tb_version = "4.3.5"

window = tk.Tk()
window.geometry("500x870")
window.resizable(False, False)
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

run_frame = tk.Frame(window)
run_frame.pack(pady=20)

run_btn = tk.Button(run_frame, bg="#4CAF50", fg="white", text="Run Tests")
run_btn.pack(side=tk.LEFT, padx=10)

#========================================================================================================================================
#Check if all files are present (exe, Help, config, etc.)
#========================================================================================================================================
if os.path.exists(os.path.join(dir_IS, "all_checks.log")):
    os.remove(os.path.join(dir_IS, "all_checks.log"))
if os.path.exists(os.path.join(dir_IS, "failures.log")):
    os.remove(os.path.join(dir_IS, "failures.log"))

all_checks = open(os.path.join(dir_IS, "all_checks.log"), "a")  #write everything that was checked + result
failures = open(os.path.join(dir_IS, "failures.log"), "a")   #write only if a check didn't pass

def check_apps():
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
def check_dirs():
    dir_IS_help = os.path.join(dir_IS, "Help")
    dir_compareto_help = os.path.join(dir_compareto, "Help")
    compare_dirs(dir_IS_help, dir_compareto_help)

    dir_IS_toolbox = os.path.join(dir_IS, "ToolboxSystem")
    dir_compareto_toolbox = os.path.join(dir_compareto, "ToolboxSystem")
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


def main():
    check_apps()
    check_dirs()


#the function check_dirs() is triggered when the "Run Tests" button is clicked
run_btn.config(command=lambda: main())

# START the GUI
window.mainloop()
