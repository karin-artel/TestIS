import os
import subprocess
import time

#directory where the IS puts Toolbox
dir_IS = "d:\\Toolbox AP\\"

#directory with Toolbox installed correctly
dir_compareto = "d:\\Toolbox\\tb_435\\"

server = "LAPTOP-HAYA\SQL2016ST"

licensed_db = "Karin_Lucy_LH"

apps = ["UserManagement.exe", "ConfigurationEditor.exe", "DatabaseChecking.exe", "DatabasePurging.exe", "DataScience.exe", 
        "FormulaEditor.exe", "HierarchyManager.exe", "ToolboxDesktop.exe", "SystemBuilder.exe", "Planner.exe", "ConfigurationEditor.exe",
        "Maintenance.exe", "LogAnalyzer.exe", "LoadData.exe", "IntegrationBuilder.exe", "BAR.exe", "ActiveUsers.exe"]   


#========================================================================================================================================
#Check if all files are present (exe, Help, config, etc.)
#========================================================================================================================================

for app in apps:
        app_path = os.path.join(dir_IS, app)
        if not os.path.exists(app_path):
                print(f"{app} not found")

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

dir_IS_toolbox = os.path.join(dir_IS, "Toolbox")
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
source_file = "d:\\Toolbox AP\\ToolboxSystem\\Data\\_ToolBoxUser.config"
dest_file = "d:\\Toolbox AP\\_ToolBoxUser.config"

with open(source_file, 'r') as file:
    content = file.read()

content = content.replace("c:\\", "d:\\")

with open(dest_file, 'w') as file:
    file.write(content)

os.remove(source_file)

#add licensed_db to Databases.config, move it to the ToolboxSystem folder
source_file = "d:\\Toolbox AP\\ToolboxSystem\\Data\\Databases.config"
dest_file = "d:\\Toolbox AP\\ToolboxSystem\\Databases.config"

with open(source_file, 'r') as file:
    content = file.read()

content = content.replace("ExampleDB", f"{licensed_db}")
content = content.replace("ExampleSqlSRV", f"{server}")

with open(dest_file, 'w') as file:
    file.write(content)

os.remove(source_file)

#run & stop all the apps. If any of them crashes, stop the script execution and report the error
for app in apps:
        app_path = os.path.join(dir_IS, app)
        subprocess.Popen(app_path)
        time.sleep(3)

        print(f"Stopping {app}...")
        app_name = app.replace(".exe", "")
        os.system(f"taskkill /IM {app} /F")