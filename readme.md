# YouTube Downloader 🎥

*A robust and minimal YouTube downloader.*

A high-performance, dark-themed desktop application for downloading YouTube videos and extracting audio. Built with Python, this tool leverages the power of `yt-dlp` for reliable media extraction and `CustomTkinter` for a sleek, modern user interface.

## ✨ Features

* **High-Quality Video Downloads**: Support for downloading videos in up to 1080p resolution (automatically merges video and audio tracks).
* **Audio Extraction**: Instantly convert and download videos as MP3 audio files.
* **Modern GUI**: A responsive, dark-mode user interface designed with `customtkinter`.
* **Real-Time Feedback**: Dynamic progress bar, exact percentage tracking, and Estimated Time of Arrival (ETA).
* **Graceful Interruption**: Safely cancel active downloads without crashing the application or corrupting files.
* **Persistent Settings**: Remembers your preferred download directory and default format using a local `config.json` file.
* **Fail-Safe Fallbacks**: Automatically adjusts to standard 720p downloads if advanced dependencies (like FFmpeg) are missing on the host machine.

_Playlist download not supported currently, this feature will be available in a future release._

## 🛠️ Technologies Used

* **[Python 3](https://www.python.org/)**: Core programming language.
* **[yt-dlp](https://github.com/yt-dlp/yt-dlp)**: The industry-standard command-line audio/video downloader.
* **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)**: UI library used to create the modern, dark-themed graphical interface.
* **[FFmpeg](https://ffmpeg.org/)**: External backend utility required for merging high-resolution video tracks and extracting high-quality MP3s.
* **[Pillow (PIL)](https://python-pillow.org/)**: Used for dynamic rendering of custom UI icons.

---

## ⚙️ Prerequisites & Setup

_If you are not a developer, you can download the executable file in releases section and double click to run it :)_

### 1. Python Environment
Ensure you have Python 3.8 or higher installed. 
Clone the repository to your local machine:

```bash
git clone https://github.com/imjanindu/youtube-downloader.git
```

Move to the app directory:
```bash
cd youtube-downloader
```

### 2. Install Python Dependencies
It is recommended to use a virtual environment. Install the required Python packages using:

```bash
pip install -r requirements.txt
```
*(Note: Ensure you regularly run `pip install -U yt-dlp` to keep the extraction engine updated against YouTube's algorithmic changes).*

### 3. Install FFmpeg (Critical for 1080p & MP3s)
YouTube streams high-quality video and audio separately. To download 1080p videos or convert files to MP3, the software requires **FFmpeg** to merge the files.
1. Download the essential FFmpeg build for Windows from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
2. Extract the archive.
3. Locate the `ffmpeg.exe` file inside the `bin/` folder.
4. Place `ffmpeg.exe` directly into the root folder of this project (in the same directory as `main.py`), or add it to your system's PATH.

## 🚀 Usage

To launch the application from the source code, run:

```bash
python main.py
```

1. **Paste** a valid YouTube URL into the input field.
2. **Select** your desired format (MP4 - 1080p, MP4 - 720p, or MP3 - Audio).
3. **Click Download**. The file will be saved to your default `Downloads` folder, or the custom path you defined in the Settings (⚙) menu.

## 📦 Building a Standalone Executable (.exe)

You can compile this Python script into a single, portable Windows executable using PyInstaller.

1. Install PyInstaller:

```bash
python -m pip install pyinstaller
```

2. Run the following compilation command from the root directory:

```bash
python -m PyInstaller --noconfirm --onefile --windowed --icon="images/icon.ico" --add-data="images;images" --collect-all customtkinter main.py
```

3. Locate your compiled application inside the newly generated `dist/` folder.
4. *Important:* Remember to place `ffmpeg.exe` in the same folder as your new executable if you want to use the 1080p or MP3 features on another computer.

## 📂 Project Structure

```text
youtube-downloader/
│
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── config.json             # Auto-generated user preferences file
├── images/                 # GUI Assets
│   ├── icon.ico            # Windows Taskbar/Window icon
│   ├── icon.png            # Tkinter fallback icon
│   └── settings.png        # Custom settings button icon
├── core/                   # Backend Logic
│   ├── downloader.py       # yt-dlp extraction engine
│   └── exceptions.py       # Custom error handling
└── ui/                     # Frontend Interface
    ├── app.py              # Main CustomTkinter window class
    └── settings_modal.py   # Settings popup window class
```

## ⚠️ Disclaimer
This software is strictly for educational purposes and personal use. Downloading copyrighted material without permission may violate YouTube's Terms of Service and local copyright laws. The developer is not responsible for any misuse of this tool.

---
**Developed by [Janindu Malshan](https://janindu.vercel.app)** - [LinkedIn](https://linkedin.com/in/imjanindu) | [GitHub](https://github.com/imjanindu)