import logging
from config import LOG_LEVEL

LOG_LEVELS = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
}

str_format = "%(asctime)s | %(levelname)s | %(message)s"
logging.basicConfig(format=str_format, level=LOG_LEVELS[LOG_LEVEL])
