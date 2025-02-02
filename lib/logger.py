import colorama
from colorama import Fore
import logging


class COLORS:
    DEBUG = Fore.LIGHTGREEN_EX
    INFO = Fore.LIGHTWHITE_EX
    WARNING = Fore.YELLOW
    ERROR = Fore.RED
    CRITICAL = Fore.LIGHTRED_EX


def get_one_format(color, app_name):
    return f"{Fore.LIGHTWHITE_EX}%(asctime)s - {app_name}{Fore.LIGHTWHITE_EX} - {color}%(levelname)s{Fore.LIGHTWHITE_EX} - %(message)s{Fore.RESET}"


def get_formats(app_name):
    return {
        logging.DEBUG: get_one_format(COLORS.DEBUG, app_name),
        logging.INFO: get_one_format(COLORS.INFO, app_name),
        logging.WARNING: get_one_format(COLORS.WARNING, app_name),
        logging.ERROR: get_one_format(COLORS.ERROR, app_name),
        logging.CRITICAL: get_one_format(COLORS.CRITICAL, app_name),
    }


class CustomFormatter(logging.Formatter):
    def __init__(self, app_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.FORMATS = get_formats(app_name)

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def create_logger(name: str, app_name: str):
    colorama.init()

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    ch.setFormatter(CustomFormatter(app_name))

    logger.addHandler(ch)
    return logger


logger = create_logger('app', f'{Fore.MAGENTA}LOGGER')

if __name__ == '__main__':
    pass
