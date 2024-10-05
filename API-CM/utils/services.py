from loguru import logger as app_logger
import os
from utils.config import get_settings

settings = get_settings()
directory_path = os.getcwd()

_frmt = "{time: YYYY-MM-DD HH:mm:ss.SSS} | {level} | {function} | {message}"
_log_dir = os.path.join(directory_path, settings.FILE_LOG_DIR)

app_logger.configure(
    handlers=[
        {
            "sink": os.path.join(_log_dir, "application.log"),
            "level": "DEBUG",
            "colorize": True,
            "format": _frmt,
            "rotation": "00:00"
        },
        {
            "sink": os.path.join(_log_dir, "application_Trace.log"),
            "colorize": True,
            "format": _frmt,
            "rotation": "00:00",
            "level": "TRACE"
        }
        ])