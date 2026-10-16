import tkinter as tk
from tkinter import messagebox, filedialog
import json
from PIL import Image, ImageTk
import os

class TextViewer(tk.Tk):
    def __init__(self, compiler, request, requestBuilder):
        super().__init__()
        self.title("EZRequests Visualizer")
        self.geometry("800x600")
        self.compiler = compiler
        self.request = request
        self.requestBuilder = requestBuilder

        self.show_headers = tk.BooleanVar(value=True)
        self.show_json = tk.BooleanVar(value=False)
        self.show_raw = tk.BooleanVar(value=False)
        self.show_text = tk.BooleanVar(value=False)
        self.show_content = tk.BooleanVar(value=False)

        self._build_buttons()
        self._build_text()
        self._build_checkboxes()
        self.refresh()

    def _build_buttons(self):
        bar = tk.Frame(self)
        bar.pack(side="top", fill="x", padx=6, pady=6)

        tk.Button(bar, text="Save Response", command=self.save_file_as).pack(side="left", padx=(0, 6))
        if self.requestBuilder.path is not None:
            tk.Button(bar, text="View Image", command=self.show_image).pack(side="left")
            tk.Button(bar, text="Save Image", command=self.save_image).pack(side="left")

    def on_closing(self):
        if self.requestBuilder.path is not None:
            os.remove(self.requestBuilder.path)
        self.destroy()

    def _build_checkboxes(self):
        bar = tk.Frame(self)
        bar.pack(side="bottom", fill="x", padx=6, pady=(0, 6))

        tk.Checkbutton(
            bar, text="Response headers",
            variable=self.show_headers, command=self.refresh,
        ).pack(side="left", padx=(0, 12))

        tk.Checkbutton(
            bar, text="Response content",
            variable=self.show_content, command=self.refresh,
        ).pack(side="left", padx=(0, 12))

        tk.Checkbutton(
            bar, text="Response JSON",
            variable=self.show_json, command=self.refresh,
        ).pack(side="left")

        tk.Checkbutton(
            bar, text="Raw response ",
            variable=self.show_raw, command=self.refresh,
        ).pack(side="left")

        tk.Checkbutton(
            bar, text="Text response ",
            variable=self.show_text, command=self.refresh,
        ).pack(side="left")

    def _build_text(self):
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        self.text = tk.Text(
            frame, wrap="word", font=("Consolas", 12),
            yscrollcommand=scrollbar.set, state="disabled",
        )
        self.text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.text.yview)

    def _json_body(self):
        try:
            return json.dumps(self.request.json(), indent=4)
        except ValueError:
            return "(response is not valid JSON)"


    def refresh(self):
        """Rebuild the displayed text based on the checkbox state."""
        # These parts are always shown
        parts = [
            f"{self.compiler.type}\n{self.compiler.url}\n\n{self.request}",
        ]

        if self.show_headers.get():
            headers = json.dumps(dict(self.request.headers), indent=4, sort_keys=True)
            parts.append(f"-----------------------RESPONSE-HEADERS------------------------\n{headers}")

        if self.show_content.get():
            parts.append(f"-----------------------RESPONSE CONTENT------------------------\n{self.request.content}")

        if self.show_json.get():
            parts.append(f"-----------------------RESPONSE JSON------------------------\n{self._json_body()}")

        if self.show_raw.get():
            parts.append(f"-----------------------RAW RESPONSE------------------------\n{self.request.raw}")

        if self.show_text.get():
            parts.append(f"-----------------------TEXT RESPONSE------------------------\n{self.request.text}")


        self.set_text("\n\n".join(parts))

    def set_text(self, content):
        """Replace the displayed text (the widget stays read-only for the user)."""
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.text.config(state="disabled")

    # ---------- Placeholder buttons ----------
    def save_file_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text File", "*.txt"), ("All files", "*.*")],
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
        self.title(f"EZRequests Visualizer - {path}")

    def _writeimg(self, path):
        with open(path, 'wb') as file:  # open the PATH, not the Response
            file.write(self.requestBuilder.output.content)  # write the body bytes
        self.path = path
        return path

    def button_two(self):
        # TODO: placeholder
        pass

    def show_image(self):
        screen = tk.Toplevel(self)
        screen.title("Image Viewer")

        opened_image = Image.open(self.requestBuilder.path)
        opened_image.thumbnail((900, 700))
        tk_image = ImageTk.PhotoImage(opened_image, master=screen)
        tk.Button(screen, text="Save Image", command=self.save_image).pack()
        image_label = tk.Label(screen, image=tk_image)
        image_label.pack(pady=10)
        image_label.image = tk_image

    def save_image(self):
        ext = "." + self.requestBuilder.path.split("\\")[-1].split(".")[1]
        initpath = self.requestBuilder.path.split("\\")[-1] + ext
        path = filedialog.asksaveasfilename(
            defaultextension=f"*{ext}",
            initialfile= initpath or f"response_image{f'.{os.path.splitext(self.requestBuilder.path)[1]}'}",
        )
        if path:
            self._writeimg(path)

    def deleteImage(self):
        os.remove(self.requestBuilder.path)
        self.requestBuilder.path = None

