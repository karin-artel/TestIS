import os
import subprocess
import sys
import time, datetime   
import tkinter as tk
import win32api
import re


#directory where the IS puts Toolbox
dir_IS = "d:\\Toolbox AP\\"

#directory with Toolbox installed correctly
dir_compareto = "d:\\Toolbox\\tb_435\\"

dir_logs = "d:\\logs\\"

server = "LAPTOP-HAYA\SQL2016ST"

licensed_db = "Karin_Lucy_LH"

apps = [ "ActiveUsers.exe", "BAR.exe", "ConfigurationEditor.exe", "DatabaseChecking.exe", 
        "DatabasePurging.exe", "DataScience.exe", "FormulaEditor.exe", "HierarchyManager.exe", 
        "IntegrationBuilder.exe", "LoadData.exe", "LogAnalyzer.exe", "Maintenance.exe", 
        "Planner.exe", "SystemBuilder.exe", "ToolboxDesktop.exe", "UserManagement.exe"]   

help_files = ["AdministrativeGuide", "DatabaseChecking", "HierarchyManager.chm", "InputFileBuilder", 
              "IntegrationBuilder", "LoadData", "MainConcept", "Maintenance", "Planner", "UserManagement"]

tb_version = "4.3.5"

#========================================================================================================================================
#Configure UI, get user input for the global parameters (directories, version, apps, help files to check)
#========================================================================================================================================
window = tk.Tk()
window.geometry()
title = tk.Label(text="Toolbox AP Installation Validation", font=("Arial", 16))
title.pack(pady=10, anchor=tk.W)

dir_IS_frame = tk.Frame(window) 
dir_IS_frame.pack(pady=20, anchor=tk.W) 
dir_IS_label = tk.Label(dir_IS_frame, width=25, text="Installation directory: ") 
dir_IS_label.pack(side = tk.LEFT, padx=10) 
dir_IS_entry = tk.Entry(dir_IS_frame, width=30) 
dir_IS_entry.pack(side = tk.LEFT, padx=10) 
dir_IS_entry.insert(0, dir_IS) 
dir_IS_error = tk.Label(dir_IS_frame, text="", fg="white") 
dir_IS_error.pack(anchor=tk.W)
dir_IS_entry.bind("<Return>", lambda e: validate_directory(dir_IS_entry, dir_IS_error, "dir_IS"))
dir_IS_entry.bind("<FocusOut>", lambda e: validate_directory(dir_IS_entry, dir_IS_error, "dir_IS"))

dir_compareto_frame = tk.Frame(window)
dir_compareto_frame.pack(pady=20, anchor=tk.W)
dir_compareto_label = tk.Label(dir_compareto_frame, width=25, text="Comparison directory: ")
dir_compareto_label.pack(side = tk.LEFT, padx=10)
dir_compareto_entry = tk.Entry(dir_compareto_frame, width=30)
dir_compareto_entry.pack(side = tk.LEFT, padx=10)
dir_compareto_entry.insert(0, dir_compareto)
dir_compareto_error = tk.Label(dir_compareto_frame, text="", fg="red")
dir_compareto_error.pack(anchor=tk.W)
dir_compareto_entry.bind("<Return>", lambda e: validate_directory(dir_compareto_entry, dir_compareto_error, "dir_compareto"))
dir_compareto_entry.bind("<FocusOut>", lambda e: validate_directory(dir_compareto_entry, dir_compareto_error, "dir_compareto"))

dir_logs_frame = tk.Frame(window)
dir_logs_frame.pack(pady=20, anchor=tk.W)
dir_logs_label = tk.Label(dir_logs_frame, width=25, text="Logs directory: ")
dir_logs_label.pack(side = tk.LEFT, padx=10)
dir_logs_entry = tk.Entry(dir_logs_frame, width=30)
dir_logs_entry.pack(side = tk.LEFT, padx=10)
dir_logs_entry.insert(0, dir_logs)
dir_logs_error = tk.Label(dir_logs_frame, text="", fg="red")
dir_logs_error.pack(anchor=tk.W)
dir_logs_entry.bind("<Return>", lambda e: validate_directory(dir_logs_entry, dir_logs_error, "dir_logs"))
dir_logs_entry.bind("<FocusOut>", lambda e: validate_directory(dir_logs_entry, dir_logs_error, "dir_logs"))

version_frame = tk.Frame(window)
version_frame.pack(pady=10, anchor=tk.CENTER)
version_label = tk.Label(version_frame, width=15, text="Toolbox version: ")
version_label.pack(side = tk.LEFT, padx=10)
version_entry = tk.Entry(version_frame, width=7)
version_entry.pack(side = tk.LEFT, padx=0)
version_entry.insert(0, tb_version)
version_entry.bind("<Return>", lambda e: validate_version())
version_entry.bind("<FocusOut>", lambda e: validate_version())
version_error_frame = tk.Frame(window)
version_error_frame.pack(pady=0, anchor=tk.E) 
version_error = tk.Label(version_error_frame, text="", fg="red")
version_error.pack()

run_frame = tk.Frame(window)
run_frame.pack(pady=20)

run_btn = tk.Button(run_frame, bg="#4CAF50", fg="white", text="Run Tests")
run_btn.pack(side=tk.LEFT, padx=10)


class TextRedirector(object):
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)  # Auto-scroll to bottom
        self.text_widget.update()

    def flush(self):
        pass


def check_all_valid():
    """Check if all inputs are valid and enable/disable Run button"""
    # Check dir_IS
    dir_IS_valid = os.path.isdir(dir_IS_entry.get().strip())
    
    # Check dir_compareto
    dir_compareto_valid = os.path.isdir(dir_compareto_entry.get().strip())
    
    # Check dir_logs
    dir_logs_valid = os.path.isdir(dir_logs_entry.get().strip())
    
    # Check version format
    version = version_entry.get().strip()
    version_valid = re.fullmatch(r"[\d.]+", version) and not version.startswith(".") and not version.endswith(".")
    
    # Enable button only if all are valid
    if dir_IS_valid and dir_compareto_valid and dir_logs_valid and version_valid:
        run_btn.config(state=tk.NORMAL, bg="#4CAF50")
    else:
        run_btn.config(state=tk.DISABLED, bg="#cccccc")


def validate_directory(entry, error_label, var_name):
    global dir_IS, dir_compareto, dir_logs

    path = entry.get().strip()

    # Automatically add backslash if missing
    if path and not path.endswith("\\"):
        path = path + "\\"
        entry.delete(0, tk.END)
        entry.insert(0, path)

    if not os.path.isdir(path):
        entry.config(bg="#ffcccc")
        #error_label.config(text="Directory does not exist")
    else:
        entry.config(bg="white")
        error_label.config(text="", fg="red")  #hide error message

        if var_name == "dir_IS":
            dir_IS = path
        elif var_name == "dir_compareto":
            dir_compareto = path
        elif var_name == "dir_logs":
            dir_logs = path
    check_all_valid()


def validate_version(event=None):
    global tb_version

    version = version_entry.get().strip()

    if not re.fullmatch(r"[\d.]+", version):
        version_entry.config(bg="#ffcccc")
        version_error.config(text="Version must contain only numbers and dots")
    elif version.startswith(".") or version.endswith("."):
        version_entry.config(bg="#ffcccc")
        version_error.config(text="Version cannot start or end with a dot")
    else:
        version_entry.config(bg="white")
        version_error.config(text="")
        tb_version = version
    check_all_valid()


def create_output_window():
    output_window = tk.Toplevel(window)
    output_window.title("Test Results")
    output_window.geometry("700x400")
    output_text = tk.Text(output_window, bg="white", fg="black", font=("Courier", 10))
    output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    old_stdout = sys.stdout     #redirect output to the text widget
    sys.stdout = TextRedirector(output_text)
#========================================================================================================================================
#Check if all files are present (exe, Help, config, etc.)
#========================================================================================================================================
def create_log_files():
    print(dir_logs)
    # Make sure the directory exists
    try:
        if not os.path.exists(dir_logs):
            os.makedirs(dir_logs)
    except Exception as e:
        print(f"Error creating directory {dir_logs}: {e}")
        return None, None
    
    # Remove old log files
    try:
        if os.path.exists(os.path.join(dir_logs, "all_checks.log")):
            os.remove(os.path.join(dir_logs, "all_checks.log"))
        if os.path.exists(os.path.join(dir_logs, "failures.log")):
            os.remove(os.path.join(dir_logs, "failures.log"))
    except Exception as e:
        print(f"Error removing old log files: {e}")
    
    # Create new log files in append mode (empty files ready for appending)
    try:
        all_checks = open(os.path.join(dir_logs, "all_checks.log"), "a")
        failures = open(os.path.join(dir_logs, "failures.log"), "a")
        return all_checks, failures
    except Exception as e:
        print(f"Error creating log files: {e}")
        return None, None


def check_apps():
    all_checks, failures = create_log_files()
    for app in apps:
        app_path = os.path.join(dir_IS, app)

        if not os.path.exists(app_path):
            print(f"{app} not found")
            all_checks.write(f"{app} not found\n")
            failures.write(f"{app} not found\n")
        else:
            try:
                info = win32api.GetFileVersionInfo(app_path, '\\')
                ms = info['FileVersionMS']
                ls = info['FileVersionLS']
                app_version = f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
            except Exception as e:
                print(f"Error getting version for {app}: {e}")                   
            
            if not app_version.startswith(tb_version):
                msg = f"{app} version mismatch: {app_version} (expected {tb_version}.x)"
                print(msg)
                all_checks.write(msg + "\n")
                failures.write(msg + "\n")
            else:
                all_checks.write(f"{app} version OK: {app_version}\n")


def compare_dirs(dir1, dir2): 
    """
    Compare files in the installation directory with a reference directory.

    The function reports:
    - missing files
    - extra files
    - file size mismatches

    It also validates that the versions of application executables
    match the expected Toolbox version (tb_version).
    """
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
    dir_name = os.path.basename(dir1)
    if mismatches:
        print(f"Files that do not match: in folder {dir_name}: ")
        for mismatch in mismatches:
            print(mismatch)
    else:
        print(f"All files match in folder {dir_name}.")


def check_dirs():
    """
    Compare key Toolbox subdirectories between the installation directory
    (dir_IS) and the reference directory (dir_compareto).

    The function verifies that files in Help, ToolboxSystem, Texts, CreateDBSql,
    and Data match between the two locations.
    """
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
    create_log_files()
    create_output_window()
    check_apps()
    check_dirs()


#the function check_dirs() is triggered when the "Run Tests" button is clicked
run_btn.config(command=lambda: main())

# START the GUI
window.mainloop()