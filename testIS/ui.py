import datetime
import os
import re
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog


class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)
        self.text_widget.update()

    def flush(self):
        pass


class TestISUI:
    def __init__(self, config, run_tests):
        self.config = config
        self.run_tests = run_tests

        self.window = tk.Tk()
        self.window.geometry()
        self.window.title("Toolbox AP Installation Validation")

        self.version_entry = None
        self.version_error = None
        self.date_entry = None
        self.date_error = None
        self.dir_IS_entry = None
        self.dir_compareto_entry = None
        self.dir_logs_entry = None
        self.run_btn = None
        self.check_all_btn = None
        self.failures_btn = None

        self.build()

    def build(self):
        title = tk.Label(
            self.window,
            text="Toolbox AP Installation Validation",
            font=("Arial", 16),
        )
        title.pack(pady=10, anchor=tk.W)

        self.build_version_row()
        self.build_date_row()
        self.dir_IS_entry = self.build_directory_row("Installation directory: ", "dir_IS")
        self.dir_compareto_entry = self.build_directory_row("Comparison directory: ", "dir_compareto")
        self.dir_logs_entry = self.build_directory_row("Logs directory: ", "dir_logs", pady=(10, 60))
        self.build_run_buttons()
        self.check_all_entries()

    def build_version_row(self):
        version_frame = tk.Frame(self.window)
        version_frame.pack(anchor=tk.E, padx=40)

        version_label = tk.Label(version_frame, width=15, anchor="e", text="Toolbox version: ")
        version_label.pack(side=tk.LEFT, padx=10)

        self.version_entry = tk.Entry(version_frame, width=7)
        self.version_entry.pack(side=tk.LEFT, padx=0)
        self.version_entry.insert(0, self.config["tb_version"])
        self.version_entry.bind("<Return>", self.validate_version)
        self.version_entry.bind("<FocusOut>", self.validate_version)

        version_error_frame = tk.Frame(self.window)
        version_error_frame.pack(pady=0, anchor=tk.E)
        self.version_error = tk.Label(version_error_frame, text="", fg="red")
        self.version_error.pack()

    def build_date_row(self):
        date_frame = tk.Frame(self.window)
        date_frame.pack(pady=5, anchor=tk.E)

        date_label = tk.Label(date_frame, anchor="e", text="Install set creation date:")
        date_label.pack(side=tk.LEFT, padx=10)

        self.date_entry = tk.Entry(date_frame, width=12)
        self.date_entry.pack(side=tk.LEFT)
        self.date_entry.insert(0, self.config["install_date"].strftime("%d-%m-%Y"))
        self.date_entry.bind("<Return>", self.validate_date)
        self.date_entry.bind("<FocusOut>", self.validate_date)

        self.date_error = tk.Label(self.window, text="", fg="red")
        self.date_error.pack(anchor=tk.E)

    def build_directory_row(self, label_text, config_key, pady=10):
        row = tk.Frame(self.window)
        row.pack(pady=pady, anchor=tk.W)

        label = tk.Label(row, width=25, text=label_text)
        label.pack(side=tk.LEFT, padx=10)

        field = tk.Frame(row, bd=1, relief=tk.SUNKEN, bg="white")
        field.pack(side=tk.LEFT, padx=10)

        entry = tk.Entry(field, width=27, bd=0)
        entry.pack(side=tk.LEFT, padx=(2, 0))
        entry.insert(0, self.config[config_key])

        error_label = tk.Label(row, text="", fg="red")
        error_label.pack(anchor=tk.W)

        browse_btn = tk.Button(
            field,
            text="...",
            width=2,
            bd=0,
            bg="white",
            activebackground="white",
            command=lambda: self.browse_directory(entry, error_label, config_key),
        )
        browse_btn.pack(side=tk.LEFT, padx=(0, 2))

        entry.bind(
            "<Return>",
            lambda event: self.validate_directory(entry, error_label, config_key),
        )
        entry.bind(
            "<FocusOut>",
            lambda event: self.validate_directory(entry, error_label, config_key),
        )

        return entry

    def build_run_buttons(self):
        run_frame = tk.Frame(self.window)
        run_frame.pack()

        self.run_btn = tk.Button(
            run_frame,
            bg="#4CAF50",
            fg="white",
            text="Run Tests",
            command=self.run_tests,
        )
        self.run_btn.pack(side=tk.LEFT, padx=10)

        logs_frame = tk.Frame(self.window)
        logs_frame.pack(pady=10)

        self.check_all_btn = tk.Button(
            logs_frame,
            text="View all_checks.log",
            state=tk.DISABLED,
            command=lambda: self.open_log_file("all_checks.log"),
        )
        self.check_all_btn.pack(side=tk.LEFT, padx=5)

        self.failures_btn = tk.Button(
            logs_frame,
            text="View failures.log",
            state=tk.DISABLED,
            command=lambda: self.open_log_file("failures.log"),
        )
        self.failures_btn.pack(side=tk.LEFT, padx=5)

    def open_log_file(self, filename):
        log_path = os.path.join(self.config["dir_logs"], filename)

        if os.path.exists(log_path) and os.path.getsize(log_path) > 0:
            subprocess.Popen(f'notepad "{log_path}"')
        else:
            print(f"Log file {filename} not found or is empty")

    def update_log_buttons(self):
        all_checks_path = os.path.join(self.config["dir_logs"], "all_checks.log")
        failures_path = os.path.join(self.config["dir_logs"], "failures.log")

        all_checks_valid = os.path.exists(all_checks_path) and os.path.getsize(all_checks_path) > 0
        failures_valid = os.path.exists(failures_path) and os.path.getsize(failures_path) > 0

        self.check_all_btn.config(state=tk.NORMAL if all_checks_valid else tk.DISABLED)
        self.failures_btn.config(state=tk.NORMAL if failures_valid else tk.DISABLED)

    def check_all_entries(self):
        dir_IS_valid = os.path.isdir(self.dir_IS_entry.get().strip())
        dir_compareto_valid = os.path.isdir(self.dir_compareto_entry.get().strip())
        dir_logs_valid = os.path.isdir(self.dir_logs_entry.get().strip())

        version = self.version_entry.get().strip()
        version_valid = (
            re.fullmatch(r"[\d.]+", version)
            and not version.startswith(".")
            and not version.endswith(".")
        )
        date_valid = True

        if dir_IS_valid and dir_compareto_valid and dir_logs_valid and version_valid and date_valid:
            self.run_btn.config(state=tk.NORMAL, bg="#4CAF50")
        else:
            self.run_btn.config(state=tk.DISABLED, bg="#cccccc")

    def browse_directory(self, entry, error_label, config_key):
        path = filedialog.askdirectory(initialdir=entry.get().strip())

        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)
            self.validate_directory(entry, error_label, config_key)

    def validate_directory(self, entry, error_label, config_key):
        path = entry.get().strip()

        if path and not path.endswith("\\"):
            path += "\\"
            entry.delete(0, tk.END)
            entry.insert(0, path)

        if not os.path.isdir(path):
            entry.config(bg="#ffcccc")
        else:
            entry.config(bg="white")
            error_label.config(text="", fg="red")
            self.config[config_key] = path

        self.check_all_entries()

    def validate_version(self, event=None):
        version = self.version_entry.get().strip()

        if not re.fullmatch(r"[\d.]+", version):
            self.version_entry.config(bg="#ffcccc")
            self.version_error.config(text="Version must contain only numbers and dots")
        elif version.startswith(".") or version.endswith("."):
            self.version_entry.config(bg="#ffcccc")
            self.version_error.config(text="Version cannot start or end with a dot")
        else:
            self.version_entry.config(bg="white")
            self.version_error.config(text="")
            self.config["tb_version"] = version

        self.check_all_entries()

    def validate_date(self, event=None):
        date_str = self.date_entry.get().strip()

        try:
            install_date = datetime.datetime.strptime(date_str, "%d-%m-%Y").date()
            self.date_entry.config(bg="white")
            self.date_error.config(text="")
            self.config["install_date"] = install_date
        except ValueError:
            self.date_entry.config(bg="#ffcccc")
            self.date_error.config(text="Use format DD-MM-YYYY")

        self.check_all_entries()

    def create_output_window(self):
        output_window = tk.Toplevel(self.window)
        output_window.title("Test Results")
        output_window.geometry("700x400")

        output_frame = tk.Frame(output_window)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(output_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        output_text = tk.Text(
            output_frame,
            bg="white",
            fg="black",
            font=("Courier", 10),
            yscrollcommand=scrollbar.set,
        )
        output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=output_text.yview)

        sys.stdout = TextRedirector(output_text)

    def start(self):
        self.window.mainloop()
