import sys
import tkinter as tk


class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)
        self.text_widget.update()

    def flush(self):
        pass


class LicenseTestUI:
    def __init__(self, run_tests):
        self.run_tests = run_tests

        self.window = tk.Tk()
        self.window.title("License Test Output")
        self.window.geometry("800x500")

        title = tk.Label(
            self.window,
            text="License Test Output",
            font=("Arial", 14),
        )
        title.pack(pady=10, anchor=tk.W, padx=10)

        output_frame = tk.Frame(self.window)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scrollbar = tk.Scrollbar(output_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.output_text = tk.Text(
            output_frame,
            bg="white",
            fg="black",
            font=("Courier", 10),
            yscrollcommand=scrollbar.set,
        )
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.output_text.yview)

        self.run_button = tk.Button(
            self.window,
            text="Run Again",
            state=tk.DISABLED,
            command=self.run_tests,
        )
        self.run_button.pack(pady=10)

        sys.stdout = TextRedirector(self.output_text)
        sys.stderr = TextRedirector(self.output_text)

    def set_finished(self):
        self.run_button.config(state=tk.NORMAL)

    def start(self):
        self.window.after(100, self.run_tests)
        self.window.mainloop()
