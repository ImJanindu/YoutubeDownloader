class YTDLPBaseException(Exception):
    """Base exception for the YouTube Downloader application."""
    pass

class DownloadCancelledException(YTDLPBaseException):
    """Raised when the user manually interrupts the download."""
    pass