import os

#directory where the IS puts Toolbox
dir_IS = "d:\\Toolbox AP\\"

#directory with Toolbox installed correctly
dir_compareto = "d:\\Toolbox\\tb_435\\"

apps = ["UserManagement.exe", "ConfigurationEditor.exe", "DatabaseChecking.exe", "DatabasePurging.exe", "DataScience.exe", 
        "FormulaEditor.exe", "HierarchyManager.exe", "ToolboxDesktop.exe", "SystemBuilder.exe", "Planner.exe", "ConfigurationEditor.exe",
        "Maintenance.exe", "LogAnalyzer.exe", "LoadData.exe", "IntegrationBuilder.exe", "BAR.exe", "ActiveUsers.exe"]   

for app in apps:
        app_path = os.path.join(dir_IS, app)
        if not os.path.exists(app_path):
                print(f"{app} not found")


#compare Helps
dir_IS_help = os.path.join(dir_IS, "Help")
dir_compareto_help = os.path.join(dir_compareto, "Help")

# Get files from both directories
files_IS = {f: os.path.getsize(os.path.join(dir_IS_help, f)) 
            for f in os.listdir(dir_IS_help) if os.path.isfile(os.path.join(dir_IS_help, f))}

files_compareto = {f: os.path.getsize(os.path.join(dir_compareto_help, f)) 
                   for f in os.listdir(dir_compareto_help) if os.path.isfile(os.path.join(dir_compareto_help, f))}

# Compare files
mismatches = []

# Check for files in dir_IS_help that don't exist in dir_compareto_help
for file, size in files_IS.items():
    if file not in files_compareto:
        mismatches.append(f"{file} - Missing in comparison directory")
    elif files_compareto[file] != size:
        mismatches.append(f"{file} - Size mismatch (IS: {size} bytes, Compare: {files_compareto[file]} bytes)")

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