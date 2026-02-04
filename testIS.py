import os

dir = "d:\\Toolbox AP\\"

apps = ["UserManagement.exe", "ConfigurationEditor.exe", "DatabaseChecking.exe", "DatabasePurging.exe", "DataScience.exe", 
        "FormulaEditor.exe", "HierarchyManager.exe", "ToolboxDesktop.exe", "SystemBuilder.exe", "Planner.exe", "ConfigurationEditor.exe",
        "Maintenance.exe", "LogAnalyzer.exe", "LoadData.exe", "IntegrationBuilder.exe", "BAR.exe", "ActiveUsers.exe"]   

for app in apps:
        app_path = os.path.join(dir, app)
        if not os.path.exists(app_path):
                print(f"{app} not found \n")