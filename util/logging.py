import os
import logging
from logging.handlers import RotatingFileHandler


os.system("")  # enable colored logs on Windows
os.makedirs("logs", exist_ok=True)


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[1;39m",
        "INFO": "\033[1;32m",
        "WARNING": "\033[1;33m",
        "ERROR": "\033[1;31m",
        "CRITICAL": "\033[1;36m",
    }
    RESET = "\x1B[0m"

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        record.msg = f"{log_color}{record.msg}{self.RESET}"
        return super().format(record)


stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(ColoredFormatter(
    fmt="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%m/%d/%y %H:%M:%S"
))

file_handler = RotatingFileHandler(
    "logs/bot.log",
    maxBytes=1 * 1024 * 1024 * 1024,  # 1GB max file size
    backupCount=5
)
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%m/%d/%y %H:%M:%S"
))

logger = logging.getLogger("discord-bot")
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
