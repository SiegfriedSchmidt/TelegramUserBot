from io import BytesIO
from typing import List
import colorama
from colorama import Fore
import logging
import sys


class COLORS:
    DEBUG = Fore.LIGHTGREEN_EX
    INFO = Fore.LIGHTWHITE_EX
    WARNING = Fore.YELLOW
    ERROR = Fore.RED
    CRITICAL = Fore.LIGHTRED_EX
    APP_NAME = Fore.MAGENTA


def get_one_format(color, app_name):
    return f"{Fore.LIGHTWHITE_EX}%(asctime)s - {COLORS.APP_NAME}{app_name}{Fore.LIGHTWHITE_EX} - {color}%(levelname)s{Fore.LIGHTWHITE_EX} - %(message)s{Fore.RESET}"


def get_formats(app_name):
    return {
        logging.DEBUG: get_one_format(COLORS.DEBUG, app_name),
        logging.INFO: get_one_format(COLORS.INFO, app_name),
        logging.WARNING: get_one_format(COLORS.WARNING, app_name),
        logging.ERROR: get_one_format(COLORS.ERROR, app_name),
        logging.CRITICAL: get_one_format(COLORS.CRITICAL, app_name),
    }


class ColoredFormatter(logging.Formatter):
    def __init__(self, app_name):
        super().__init__()
        self.formats = get_formats(app_name)

    def format(self, record):
        log_fmt = self.formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


class PlainFormatter(logging.Formatter):
    def __init__(self, app_name):
        fmt = f"%(asctime)s - {app_name} - %(levelname)s - %(message)s"
        super().__init__(fmt, "%Y-%m-%d %H:%M:%S")


class LogStream:
    def __init__(self):
        self.logs: List[str] = []

    def write(self, string: str):
        if string.strip():
            self.logs.append(string)

    def flush(self):
        pass

    def get_file(self) -> BytesIO:
        file = BytesIO(str(self).encode("utf-8"))
        file.name = 'logs.txt'
        return file

    def __str__(self):
        return "".join(self.logs)


def create_logger(name: str, app_name: str):
    colorama.init()

    # Init logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create custom stream
    log_stream = LogStream()

    # Create handlers
    terminal_handler = logging.StreamHandler(sys.stdout)
    log_stream_handler = logging.StreamHandler(log_stream)

    # Set formatters
    terminal_handler.setFormatter(ColoredFormatter(app_name))
    log_stream_handler.setFormatter(PlainFormatter(app_name))

    # Add handlers
    logger.addHandler(terminal_handler)
    logger.addHandler(log_stream_handler)

    return logger, log_stream


logger, log_stream = create_logger('app', f'LOGGER')

if __name__ == '__main__':
    pass
