import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

class TextEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EZ Requests editor")
        self.geometry("800x600")
        self.current_file = None

        self._build_menu()
        self._build_editor()
        self._build_statusbar()
        self._bind_events()
        self.update_line_numbers()

    # ---------- UI ----------
    def _build_menu(self):
        menubar = tk.Menu(self)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        # Run button sits right next to the File menu
        menubar.add_command(label="Run", command=self.run_code)

        self.config(menu=menubar)

    def _build_editor(self):
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True)

        self.line_numbers = tk.Text(
            frame, width=5, padx=4, takefocus=0, border=0,
            background="#f0f0f0", foreground="#666666",
            state="disabled", wrap="none", font=("Consolas", 12),
        )
        self.line_numbers.pack(side="left", fill="y")

        self.scrollbar = tk.Scrollbar(frame, command=self._on_scrollbar)
        self.scrollbar.pack(side="right", fill="y")

        self.text = tk.Text(
            frame, wrap="none", undo=True, font=("Consolas", 12),
            yscrollcommand=self._on_text_scroll,
        )
        self.text.pack(side="left", fill="both", expand=True)

    def _build_statusbar(self):
        self.status = tk.Label(self, text="Lines: 1", anchor="w", relief="sunken")
        self.status.pack(side="bottom", fill="x")

    def _bind_events(self):
        self.text.bind("<<Modified>>", self._on_modified)
        self.text.bind("<KeyRelease>", lambda e: self.update_line_numbers())
        self.bind("<Control-n>", lambda e: self.new_file())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-S>", lambda e: self.save_file_as())

    # ---------- Scrolling / line numbers ----------
    def _on_scrollbar(self, *args):
        self.text.yview(*args)
        self.line_numbers.yview(*args)

    def _on_text_scroll(self, first, last):
        self.scrollbar.set(first, last)
        self.line_numbers.yview_moveto(first)

    def _on_modified(self, event=None):
        if self.text.edit_modified():
            self.update_line_numbers()
            self.text.edit_modified(False)

    def update_line_numbers(self):
        line_count = int(self.text.index("end-1c").split(".")[0])
        numbers = "\n".join(str(i) for i in range(1, line_count + 1))

        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", "end")
        self.line_numbers.insert("1.0", numbers)
        self.line_numbers.config(state="disabled")
        self.line_numbers.yview_moveto(self.text.yview()[0])

        self.status.config(text=f"Lines: {line_count}")

    # ---------- File operations ----------
    def new_file(self):
        self.text.delete("1.0", "end")
        self.current_file = None
        self.title("Simple Text Editor - Untitled")
        self.update_line_numbers()

    def open_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("EZQ", "*.ezq"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{e}")
            return
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.current_file = path
        self.title(f"Simple Text Editor - {path}")
        self.update_line_numbers()

    def save_file(self):
        if self.current_file:
            self._write(self.current_file)
        else:
            self.save_file_as()

    def save_file_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".ezq",
            filetypes=[("EZRequest File", "*.ezq"), ("All files", "*.*")],
        )
        if path:
            self._write(path)

    def _write(self, path):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.text.get("1.0", "end-1c"))
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\n{e}")
            return
        self.current_file = path
        self.title(f"Simple Text Editor - {path}")

    # ---------- Run button ----------
    def run_code(self):
        if self.current_file is not None:
            if os.path.exists(self.current_file):
                self.save_file()
                subprocess.run(['python3','EZRequests.py',self.current_file])
            else:
                messagebox.showerror("Error", f"{self.current_file} Not Found")
        else:
            messagebox.showerror("Error", f"File must be saved in order to run")


if __name__ == "__main__":
    TextEditor().mainloop()