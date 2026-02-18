import os
import re
import shutil
import yt_dlp
from typing import Callable
from core.exceptions import DownloadCancelledException

class YouTubeDownloaderEngine:
    def __init__(self, download_path: str):
        self.download_path = download_path
        self._is_cancelled = False
        self.log_callback = None 

    def cancel(self):
        self._is_cancelled = True

    def _is_ffmpeg_installed(self):
        return shutil.which("ffmpeg") is not None

    def download(self, url: str, format_choice: str, progress_callback: Callable[[dict], None]) -> str:
        self._is_cancelled = False
        has_ffmpeg = self._is_ffmpeg_installed()
        
        if not has_ffmpeg and self.log_callback:
            if "1080p" in format_choice or "MP3" in format_choice:
                self.log_callback("Note: FFmpeg not found. Using standard quality.")

        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

        def internal_hook(d: dict):
            if self._is_cancelled:
                raise DownloadCancelledException("Download cancelled by user.")
            progress_callback(d)

        class ExtractionLogger:
            def __init__(self, engine):
                self.engine = engine

            def _clean(self, msg):
                msg = ansi_escape.sub('', msg)
                return msg.replace("[debug] ", "").replace("[youtube] ", "").replace("[info] ", "").replace("[error] ", "").strip()

            def debug(self, msg):
                if self.engine._is_cancelled: raise Exception("Download cancelled by user.")
                if self.engine.log_callback and "Downloading" in msg:
                    self.engine.log_callback(self._clean(msg)[:60])

            def warning(self, msg):
                if self.engine._is_cancelled: raise Exception("Download cancelled by user.")

            def error(self, msg):
                if self.engine._is_cancelled: raise Exception("Download cancelled by user.")
                if self.engine.log_callback:
                    self.engine.log_callback(f"Error: {self._clean(msg)[:60]}")

            def info(self, msg):
                if self.engine._is_cancelled: raise Exception("Download cancelled by user.")

        ydl_opts = {
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'progress_hooks': [internal_hook],
            'logger': ExtractionLogger(self),
            'socket_timeout': 30,
            'retries': 10,
            'noplaylist': True, 
            'quiet': False, 
            'no_warnings': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['web', 'default']
                }
            }
        }

        if format_choice == "MP3 - Audio":
            if has_ffmpeg:
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
                })
            else:
                ydl_opts.update({'format': 'bestaudio/best'})
        elif format_choice == "MP4 - 1080p":
            if has_ffmpeg:
                ydl_opts.update({
                    'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best',
                    'merge_output_format': 'mp4'
                })
            else:
                ydl_opts.update({'format': 'best[ext=mp4]/best'})
        else: 
            if has_ffmpeg:
                ydl_opts.update({
                    'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]/best',
                    'merge_output_format': 'mp4' 
                })
            else:
                ydl_opts.update({'format': 'best[ext=mp4]/best'})

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info_dict)
                
                if format_choice == "MP3 - Audio":
                    filename = os.path.splitext(filename)[0] + '.mp3'
                else:
                    filename = os.path.splitext(filename)[0] + '.mp4'
                    
                return filename
                
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e).lower()
            if "cancelled by user" in error_msg:
                raise DownloadCancelledException("Download cancelled by user.")
            else:
                clean_error = ansi_escape.sub('', str(e))
                raise Exception(f"{clean_error.split(';')[0][:80]}")