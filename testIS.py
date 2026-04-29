import os
import subprocess
import sys
import time, datetime   
import tkinter as tk
from tkinter import filedialog
import win32api
import win32con
import re



#directory where the IS puts Toolbox
dir_IS = "c:\\Toolbox AP\\"

#directory with Toolbox installed correctly
dir_compareto = "c:\\"

dir_logs = "c:\\logs\\"

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

version_frame = tk.Frame(window)
version_frame.pack(anchor=tk.E, padx=40)
version_label = tk.Label(version_frame, width=15, anchor="e", text="Toolbox version: ")
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

date_frame = tk.Frame(window)
date_frame.pack(pady=5, anchor=tk.E)
date_label = tk.Label(date_frame, anchor="e", text="Install set creation date:")
date_label.pack(side=tk.LEFT, padx=10)
date_entry = tk.Entry(date_frame, width=12)
date_entry.pack(side=tk.LEFT)
date_error = tk.Label(window, text="", fg="red")
date_error.pack(anchor=tk.E)
date_entry.bind("<Return>", lambda e: validate_date())
date_entry.bind("<FocusOut>", lambda e: validate_date())

dir_IS_frame = tk.Frame(window) 
dir_IS_frame.pack(pady=10, anchor=tk.W) 
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
dir_compareto_frame.pack(pady=10, anchor=tk.W)
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
dir_logs_frame.pack(pady=(10, 60), anchor=tk.W)
dir_logs_label = tk.Label(dir_logs_frame, width=25, text="Logs directory: ")
dir_logs_label.pack(side = tk.LEFT, padx=10)
dir_logs_entry = tk.Entry(dir_logs_frame, width=30)
dir_logs_entry.pack(side = tk.LEFT, padx=10)
dir_logs_entry.insert(0, dir_logs)
dir_logs_error = tk.Label(dir_logs_frame, text="", fg="red")
dir_logs_error.pack(anchor=tk.W)
dir_logs_entry.bind("<Return>", lambda e: validate_directory(dir_logs_entry, dir_logs_error, "dir_logs"))
dir_logs_entry.bind("<FocusOut>", lambda e: validate_directory(dir_logs_entry, dir_logs_error, "dir_logs"))

run_frame = tk.Frame(window)
run_frame.pack()
run_btn = tk.Button(run_frame, bg="#4CAF50", fg="white", text="Run Tests")
run_btn.pack(side=tk.LEFT, padx=10)

logs_frame = tk.Frame(window)
logs_frame.pack(pady=10)
check_all_btn = tk.Button(logs_frame, text="View all_checks.log", state=tk.DISABLED, command=lambda: open_log_file("all_checks.log"))
check_all_btn.pack(side=tk.LEFT, padx=5)
failures_btn = tk.Button(logs_frame, text="View failures.log", state=tk.DISABLED, command=lambda: open_log_file("failures.log"))
failures_btn.pack(side=tk.LEFT, padx=5)

#Log files, set to None, created in create_log_files()
all_checks = None
failures = None


#=========================================================================================================================================
#UI classes and functions
#=========================================================================================================================================
#Class to redirect print to output window in the GUI
class TextRedirector(object):
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)  # Auto-scroll to bottom
        self.text_widget.update()

    def flush(self):
        pass


def open_log_file(filename):
    """Open log file with default application"""
    log_path = os.path.join(dir_logs, filename)
    if os.path.exists(log_path) and os.path.getsize(log_path) > 0:
        import subprocess
        subprocess.Popen(f'notepad "{log_path}"')  # Opens with Notepad on Windows
    else:
        print(f"Log file {filename} not found or is empty")


def update_log_buttons():
    """Enable log buttons if files exist and are non-empty"""
    all_checks_path = os.path.join(dir_logs, "all_checks.log")
    failures_path = os.path.join(dir_logs, "failures.log")
    
    all_checks_valid = os.path.exists(all_checks_path) and os.path.getsize(all_checks_path) > 0
    failures_valid = os.path.exists(failures_path) and os.path.getsize(failures_path) > 0
    
    check_all_btn.config(state=tk.NORMAL if all_checks_valid else tk.DISABLED)
    failures_btn.config(state=tk.NORMAL if failures_valid else tk.DISABLED)


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
    date_valid = True
    try:
        datetime.strptime(date_entry.get().strip(), "%d-%m-%Y")
    except ValueError:
        date_valid = False
    
    # Enable button only if all are valid
    if dir_IS_valid and dir_compareto_valid and dir_logs_valid and version_valid and date_valid:
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


def validate_date(event=None):
    global install_date

    date_str = date_entry.get().strip()

    try:
        datetime.strptime(date_str, "%d-%m-%Y")
        date_entry.config(bg="white")
        date_error.config(text="")
        install_date = date_str
    except ValueError:
        date_entry.config(bg="#ffcccc")
        date_error.config(text="Use format DD-MM-YYYY")

    check_all_valid()


def create_output_window():
    output_window = tk.Toplevel(window)
    output_window.title("Test Results")
    output_window.geometry("700x400")
    output_frame = tk.Frame(output_window)
    output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    scrollbar = tk.Scrollbar(output_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    # Create text widget and link to scrollbar
    output_text = tk.Text(output_frame, bg="white", fg="black", font=("Courier", 10), yscrollcommand=scrollbar.set)
    output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=output_text.yview)
    old_stdout = sys.stdout     #redirect output to the text widget
    sys.stdout = TextRedirector(output_text)

#========================================================================================================================================
#Functions to check the installation: compare directories, print results & write to log files
#========================================================================================================================================
def create_log_files():
    global all_checks, failures
    
    # Make sure the directory exists
    try:
        if not os.path.exists(dir_logs):
            os.makedirs(dir_logs)
    except Exception as e:
        print(f"Error creating directory {dir_logs}: {e}")
        return False
    
    # Remove old log files
    try:
        if os.path.exists(os.path.join(dir_logs, "all_checks.log")):
            os.remove(os.path.join(dir_logs, "all_checks.log"))
        if os.path.exists(os.path.join(dir_logs, "failures.log")):
            os.remove(os.path.join(dir_logs, "failures.log"))
    except Exception as e:
        print(f"Error removing old log files: {e}")
    
    # Create new log files in append mode
    try:
        all_checks = open(os.path.join(dir_logs, "all_checks.log"), "a")
        failures = open(os.path.join(dir_logs, "failures.log"), "a")
        return True
    except Exception as e:
        print(f"Error creating log files: {e}")
        return False
        

def check_apps(all_checks, failures):
    for app in apps:
        app_path = os.path.join(dir_IS, app)

        if not os.path.exists(app_path):
            msg = f"{app} not found"
            print(msg)
            all_checks.write(msg + "\n")
            failures.write(msg + "\n")
            continue

        try:
            info = win32api.GetFileVersionInfo(app_path, '\\')
            ms = info['FileVersionMS']
            ls = info['FileVersionLS']
            app_version = f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
        except Exception as e:
            msg = f"{app} error reading version: {e}"
            print(msg)
            all_checks.write(msg + "\n")
            failures.write(msg + "\n")
            continue

        # version check
        version_ok = app_version.startswith(tb_version)

        # icon check
        icon_ok = has_icon(app_path)

        # build message
        parts = []

        if version_ok:
            parts.append(f"version OK: {app_version}")
        else:
            parts.append(f"version mismatch: {app_version} (expected {tb_version}.x)")

        if icon_ok:
            parts.append("has an icon")
        else:
            parts.append("no icon")

        msg = f"{app} " + ", ".join(parts)

        print(msg)
        all_checks.write(msg + "\n")

        if not version_ok or not icon_ok:
            failures.write(msg + "\n")

    print()
    all_checks.write("\n")
    failures.write("\n")

    all_checks.flush()
    failures.flush()


def has_icon(exe_path):
    try:
        hmodule = win32api.LoadLibraryEx(
            exe_path,
            0,
            win32con.LOAD_LIBRARY_AS_DATAFILE
        )

        icons = win32api.EnumResourceNames(hmodule, win32con.RT_GROUP_ICON)
        return len(icons) > 0

    except Exception:
        return False



def compare_dirs(dir1, dir2, all_checks, failures):
    """
    Compare files in the installation directory with a reference directory.
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

    dir_name = os.path.basename(dir1)
    if mismatches:
        print(f"Files that do not match: in folder {dir_name}: ")
        all_checks.write(f"Files that do not match: in folder {dir_name}:\n")
        for mismatch in mismatches:
            print(mismatch)
            all_checks.write(f"{mismatch}\n")
            failures.write(f"{mismatch}\n")
    else:
        msg = f"All files match in folder {dir_name}."
        print(msg)
        all_checks.write(f"{msg}\n")
    print()
    all_checks.write("\n")
    failures.write("\n")
    all_checks.flush()
    failures.flush()


def check_dirs(all_checks, failures):
    """
    Compare key Toolbox subdirectories between the installation directory
    (dir_IS) and the reference directory (dir_compareto).
    """
    dir_IS_help = os.path.join(dir_IS, "Help")
    dir_compareto_help = os.path.join(dir_compareto, "Help")
    compare_dirs(dir_IS_help, dir_compareto_help, all_checks, failures)

    dir_IS_toolbox = os.path.join(dir_IS, "ToolboxSystem")
    dir_compareto_toolbox = os.path.join(dir_compareto, "ToolboxSystem")
    compare_dirs(dir_IS_toolbox, dir_compareto_toolbox, all_checks, failures)

    dir_IS_texts = os.path.join(dir_IS, "ToolboxSystem\\Texts\\en-Us")
    dir_compareto_texts = os.path.join(dir_compareto, "ToolboxSystem\\Texts\\en-Us")
    compare_dirs(dir_IS_texts, dir_compareto_texts, all_checks, failures)

    dir_IS_sql = os.path.join(dir_IS, "CreateDBSql")
    dir_compareto_sql = os.path.join(dir_compareto, "CreateDBSql")
    compare_dirs(dir_IS_sql, dir_compareto_sql, all_checks, failures)

    dir_IS_data = os.path.join(dir_IS, "ToolboxSystem\\Data")
    dir_compareto_data = os.path.join(dir_compareto, "ToolboxSystem\\Data")
    compare_dirs(dir_IS_data, dir_compareto_data, all_checks, failures)



def main():
    if not create_log_files():
        print("Failed to create log files")
        return
    
    create_output_window()
    check_apps(all_checks, failures)
    check_dirs(all_checks, failures)
    
    all_checks.close()
    failures.close()
    
    update_log_buttons()
    print("\n✓ All checks complete!")


#the function check_dirs() is triggered when the "Run Tests" button is clicked
run_btn.config(command=lambda: main())

# START the GUI
window.mainloop()