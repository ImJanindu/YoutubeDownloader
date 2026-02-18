import customtkinter as ctk
import tkinter as tk
import threading
import os
import sys
import json
import webbrowser
import ctypes  
from PIL import Image  # Required for loading custom UI icons

from ui.settings_modal import SettingsModal
from core.downloader import YouTubeDownloaderEngine
from core.exceptions import DownloadCancelledException

CONFIG_FILE = "config.json"

# --- TASKBAR ICON FIX ---
try:
    if sys.platform == "win32":
        myappid = 'janindu.youtube.downloader.1.0' 
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Downloader")
        
        # --- Window Centering Logic ---
        app_width = 550
        app_height = 520
        
        # Fetch the user's screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate the X and Y coordinates to perfectly center the window
        center_x = int((screen_width / 2) - (app_width / 2))
        center_y = int((screen_height / 2) - (app_height / 2))
        
        # Apply the geometry dynamically
        self.geometry(f"{app_width}x{app_height}+{center_x}+{center_y}")
        self.resizable(False, False)
        
        # --- Universal Typography Setup ---
        self.font_title = ctk.CTkFont(family="Ubuntu", size=26, weight="bold")
        self.font_label = ctk.CTkLabel(self, font=ctk.CTkFont(family="Ubuntu", size=16, weight="bold")).cget("font")
        self.font_input = ctk.CTkFont(family="Ubuntu", size=15, weight="bold")
        self.font_button_main = ctk.CTkFont(family="Ubuntu", size=18, weight="bold")
        self.font_status = ctk.CTkFont(family="Ubuntu", size=14, weight="bold")
        self.font_small = ctk.CTkFont(family="Ubuntu", size=13)
        
        # --- Prominent Footer Typography ---
        self.font_footer = ctk.CTkFont(family="Ubuntu", size=16, weight="bold") 
        
        # --- Determine Base Path for Assets ---
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # Fallback to current working directory if not packaged
            if not os.path.exists(os.path.join(base_dir, 'images/icon.png')):
                base_dir = os.getcwd()
                
        self.icon_path_ico = os.path.join(base_dir, 'images/icon.ico')
        self.icon_path_png = os.path.join(base_dir, 'images/icon.png')
            
        # --- Robust App Window Icon Initialization ---
        try:
            if sys.platform == "win32" and os.path.exists(self.icon_path_ico):
                self.iconbitmap(self.icon_path_ico)
            elif os.path.exists(self.icon_path_png):
                self.app_icon = tk.PhotoImage(file=self.icon_path_png)
                self.iconphoto(True, self.app_icon)
        except Exception as e:
            print(f"Main Icon Loading Error: {e}")

        # --- Settings Button Custom Icon Initialization ---
        self.settings_image = None
        settings_png_path = os.path.join(base_dir, 'images/settings.png')
        settings_ico_path = os.path.join(base_dir, 'images/settings.ico')
        
        try:
            # Prefer PNG for UI widgets (better transparency), fallback to ICO
            if os.path.exists(settings_png_path):
                # Scale to 24x24 to perfectly fit the 30x30 button boundaries
                self.settings_image = ctk.CTkImage(light_image=Image.open(settings_png_path), size=(24, 24))
            elif os.path.exists(settings_ico_path):
                self.settings_image = ctk.CTkImage(light_image=Image.open(settings_ico_path), size=(24, 24))
        except Exception as e:
            print(f"Settings Icon Loading Error: {e}")
        
        # Load persisted settings (Path and Format)
        self.download_path, self.default_format = self.load_config()
        
        self.downloader = YouTubeDownloaderEngine(self.download_path)
        self.downloader.log_callback = self._extraction_log_hook
        
        self._build_ui()

    def load_config(self):
        default_path = os.path.join(os.path.expanduser('~\\Downloads'))
        default_format = "MP4 - 1080p"
        
        if not os.path.exists(default_path):
            os.makedirs(default_path, exist_ok=True)
            
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    return data.get("download_path", default_path), data.get("default_format", default_format)
            except Exception:
                return default_path, default_format
        return default_path, default_format

    def save_config(self):
        data = {
            "download_path": self.download_path,
            "default_format": self.default_format
        }
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def _build_ui(self):
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(20, 10), padx=30)
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="YouTube Downloader", font=self.font_title, text_color="#D32F2F")
        self.title_label.pack(side="left")

        # --- Dynamically assign the custom settings image, fallback to "⚙" if file is missing ---
        self.settings_btn = ctk.CTkButton(
            self.header_frame, 
            text="" if self.settings_image else "⚙", 
            image=self.settings_image,
            font=self.font_title, 
            width=30, height=30, 
            fg_color="transparent", 
            hover_color="#333333", 
            command=self.open_settings
        )
        self.settings_btn.pack(side="right")

        self.url_label = ctk.CTkLabel(self, text="Video URL", font=self.font_label)
        self.url_label.pack(anchor="w", padx=30)

        self.url_entry = ctk.CTkEntry(self, placeholder_text="Paste YouTube link here...", font=self.font_input, width=490, height=45)
        self.url_entry.pack(pady=(5, 15), padx=30)

        self.format_label = ctk.CTkLabel(self, text="Download Format", font=self.font_label)
        self.format_label.pack(anchor="w", padx=30)

        self.format_var = ctk.StringVar(value=self.default_format)
        self.format_segmented = ctk.CTkSegmentedButton(
            self, values=["MP4 - 1080p", "MP4 - 720p", "MP3 - Audio"], variable=self.format_var,
            font=self.font_input, width=490, height=40, selected_color="#D32F2F", selected_hover_color="#B71C1C"
        )
        self.format_segmented.pack(pady=(5, 20), padx=30)

        self.download_btn = ctk.CTkButton(self, text="Download", font=self.font_button_main, command=self.start_download, width=490, height=50, fg_color="#1A8E2F", hover_color="#136E24")
        self.download_btn.pack(pady=(0, 20), padx=30)

        # --- Progress Section ---
        self.progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        
        self.status_container = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        self.status_container.pack(fill="x", side="top", pady=(0, 5))

        self.status_label = ctk.CTkLabel(self.status_container, text="", font=self.font_status)
        self.status_label.pack(side="left")
        
        self.percentage_label = ctk.CTkLabel(self.status_container, text="0%", font=self.font_status)
        self.percentage_label.pack(side="right")

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=490, height=12, progress_color="#D32F2F")
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(5, 10))

        self.eta_label = ctk.CTkLabel(self.progress_frame, text="Estimated time: --", font=self.font_small, text_color="gray")
        self.eta_label.pack(anchor="w")

        self.cancel_btn = ctk.CTkButton(self.progress_frame, text="✕ Cancel Download", font=self.font_input, command=self.cancel_download, width=490, height=35, fg_color="transparent", border_width=1)

        self.footer_label = ctk.CTkLabel(self, text="Developed by Janindu Malshan", font=self.font_footer, text_color="gray", cursor="hand2")
        self.footer_label.pack(side="bottom", pady=10)
        self.footer_label.bind("<Button-1>", lambda e: webbrowser.open("https://janindu.vercel.app")) 

    def open_settings(self):
        SettingsModal(self, self.download_path, self.default_format, self.icon_path_ico, self.update_settings)

    def update_settings(self, new_path, new_format):
        self.download_path = new_path
        self.downloader.download_path = new_path
        
        self.default_format = new_format
        self.format_var.set(new_format)
        
        self.save_config()

    def _extraction_log_hook(self, msg):
        self.after(0, self.status_label.configure, {"text": f"Status: {msg}", "text_color": "#BB86FC"})

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            self.show_error("Please enter a valid YouTube URL.")
            return

        self.download_btn.configure(state="disabled")
        self.format_segmented.configure(state="disabled")
        self.url_entry.configure(state="disabled")
        
        self.progress_frame.pack(fill="x", padx=30, pady=(0, 10))
        self.status_container.pack(fill="x", side="top", pady=(0, 5)) 
        self.status_label.pack(side="left") 
        self.percentage_label.pack(side="right") 
        self.progress_bar.pack(pady=(5, 10))
        self.eta_label.pack(anchor="w")
        
        self.status_label.configure(text="Extracting video info...", text_color="white", justify="left", anchor="w")
        self.progress_bar.set(0)
        self.percentage_label.configure(text="0%")
        self.eta_label.configure(text="Estimated time: calculating...")
        
        self.cancel_btn.pack(pady=(10, 0))
        self.cancel_btn.configure(state="normal")
        
        threading.Thread(target=self._download_worker, args=(url, self.format_var.get()), daemon=True).start()

    def _download_worker(self, url, format_choice):
        try:
            filepath = self.downloader.download(url, format_choice, self._progress_hook)
            self.after(0, self.download_complete, filepath)
        except DownloadCancelledException:
            self.after(0, self.show_error, "Download cancelled successfully.", "orange")
        except Exception as e:
            self.after(0, self.show_error, str(e))

    def _progress_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            
            fraction = downloaded / total_bytes if total_bytes > 0 else 0
            percent_str = f"{fraction * 100:.1f}%" if total_bytes > 0 else "Downloading..."
            eta_str = f"{d.get('eta', 0)} sec" if d.get('eta') is not None else "Unknown"

            self.after(0, self.update_progress_ui, fraction, percent_str, eta_str)

        elif d['status'] == 'finished':
            self.after(0, self.status_label.configure, {"text": "Processing file... Please wait.", "text_color": "#BB86FC"})

    def update_progress_ui(self, fraction, percentage_str, eta_str):
        self.progress_bar.set(fraction)
        self.percentage_label.configure(text=percentage_str)
        self.eta_label.configure(text=f"Estimated time: {eta_str}")
        
        if self.status_label.cget("text") != "Downloading...":
            self.status_label.configure(text="Downloading...", text_color="white")

    def cancel_download(self):
        self.status_label.configure(text="Cancelling... Please wait.", text_color="orange")
        self.cancel_btn.configure(state="disabled")
        self.downloader.cancel()

    def show_error(self, message, color="#CF6679"):
        self.progress_frame.pack(fill="x", padx=30, pady=(0, 10))
        
        self.percentage_label.pack_forget() 
        self.progress_bar.pack_forget()
        self.eta_label.pack_forget()
        self.cancel_btn.pack_forget()

        self.status_label.pack_forget()
        self.status_label.pack(side="top", fill="x", expand=True)
        self.status_label.configure(
            text=message, 
            text_color=color, 
            wraplength=480, 
            justify="center", 
            anchor="center"
        )
        
        self.download_btn.configure(state="normal")
        self.format_segmented.configure(state="normal")
        self.url_entry.configure(state="normal")

    def download_complete(self, filepath):
        self.status_label.configure(text="Download finished successfully!", text_color="#03DAC6", justify="left", anchor="w")
        self.progress_bar.set(1)
        self.percentage_label.configure(text="100%")
        self.eta_label.configure(text="Done.")
        self.cancel_btn.pack_forget()
        
        self.download_btn.configure(state="normal")
        self.format_segmented.configure(state="normal")
        self.url_entry.configure(state="normal")
        
        if sys.platform == "win32":
            os.startfile(os.path.dirname(filepath))