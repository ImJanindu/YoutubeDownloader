import customtkinter as ctk
from tkinter import filedialog
import os
import sys
import webbrowser

class SettingsModal(ctk.CTkToplevel):
    def __init__(self, parent, current_path: str, current_format: str, icon_path: str, save_callback):
        super().__init__(parent)
        self.title("Settings")
        
        # Increased height to accommodate the new subtitle text
        width = 480
        height = 440 
        
        parent.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        center_x = parent_x + (parent_width // 2) - (width // 2)
        center_y = parent_y + (parent_height // 2) - (height // 2)
        
        self.geometry(f"{width}x{height}+{center_x}+{center_y}")
        self.resizable(False, False)
        
        # --- FIX: Explicit Icon Assignment for Toplevel Windows ---
        if sys.platform == "win32" and icon_path and os.path.exists(icon_path):
            self.after(200, lambda: self.iconbitmap(icon_path))
        
        self.transient(parent)
        self.grab_set()

        self.current_path = current_path
        self.current_format = current_format
        self.save_callback = save_callback
        
        # --- Typography Setup ---
        self.font_bold = ctk.CTkFont(family="Ubuntu", size=15, weight="bold")
        self.font_button = ctk.CTkFont(family="Ubuntu", size=16, weight="bold")
        self.font_small = ctk.CTkFont(family="Ubuntu", size=13)
        self.font_subtitle = ctk.CTkFont(family="Ubuntu", size=14, slant="italic") # Added for the catchphrase

        self._build_ui()

    def _build_ui(self):
        # --- App Subtitle / Catchphrase ---
        self.subtitle_label = ctk.CTkLabel(self, text="A robust and minimal YouTube downloader.", font=self.font_subtitle, text_color="gray")
        self.subtitle_label.pack(anchor="w", padx=20, pady=(15, 0))

        # --- Directory Selection ---
        self.path_label = ctk.CTkLabel(self, text="Download Location", font=self.font_bold)
        self.path_label.pack(anchor="w", padx=20, pady=(15, 5))

        self.path_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.path_frame.pack(fill="x", padx=20)

        self.path_entry = ctk.CTkEntry(self.path_frame, font=self.font_bold)
        self.path_entry.insert(0, self.current_path)
        self.path_entry.configure(state="readonly")
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.browse_btn = ctk.CTkButton(self.path_frame, text="Browse", font=self.font_bold, width=60, command=self.browse_folder)
        self.browse_btn.pack(side="right")

        # --- Default Download Format ---
        self.format_label = ctk.CTkLabel(self, text="Default Download Format", font=self.font_bold)
        self.format_label.pack(anchor="w", padx=20, pady=(15, 5))

        self.format_var = ctk.StringVar(value=self.current_format)
        self.format_dropdown = ctk.CTkOptionMenu(
            self, 
            values=["MP4 - 1080p", "MP4 - 720p", "MP3 - Audio"],
            variable=self.format_var,
            font=self.font_bold,
            fg_color="#1E1E1E",
            button_color="#333333",
            button_hover_color="#444444"
        )
        self.format_dropdown.pack(fill="x", padx=20)

        # --- Software Information ---
        self.info_label = ctk.CTkLabel(self, text="Software Version", font=self.font_bold)
        self.info_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.version_label = ctk.CTkLabel(self, text="v1.0.0 (Released: February 18, 2026)", font=self.font_small, text_color="gray")
        self.version_label.pack(anchor="w", padx=20)

        # --- Professional Connection Section ---
        self.connect_label = ctk.CTkLabel(self, text="Connect with Developer", font=self.font_bold)
        self.connect_label.pack(anchor="w", padx=20, pady=(15, 5))

        self.social_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.social_frame.pack(fill="x", padx=20)

        self.linkedin_btn = ctk.CTkButton(
            self.social_frame, text="LinkedIn", font=self.font_bold, 
            fg_color="#1E1E1E", hover_color="#333333", border_width=1, border_color="#333333", 
            command=lambda: webbrowser.open("https://linkedin.com/in/imjanindu")
        )
        self.linkedin_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.github_btn = ctk.CTkButton(
            self.social_frame, text="GitHub", font=self.font_bold, 
            fg_color="#1E1E1E", hover_color="#333333", border_width=1, border_color="#333333", 
            command=lambda: webbrowser.open("https://github.com/imjanindu")
        )
        self.github_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))

        # --- Save Button ---
        self.save_btn = ctk.CTkButton(self, text="Done", font=self.font_button, command=self.save_and_close, fg_color="#D32F2F", hover_color="#B71C1C")
        self.save_btn.pack(side="bottom", pady=20, padx=20, anchor="e")

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.current_path)
        if folder:
            self.current_path = folder
            self.path_entry.configure(state="normal")
            self.path_entry.delete(0, 'end')
            self.path_entry.insert(0, self.current_path)
            self.path_entry.configure(state="readonly")

    def save_and_close(self):
        # Pass both path and newly selected format back to the main app
        self.save_callback(self.current_path, self.format_var.get())
        self.destroy()