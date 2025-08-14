import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL_CONSOLE = getattr(logging, os.getenv("LOG_LEVEL_CONSOLE", "INFO").upper(), logging.INFO)
LOG_LEVEL_FILE = getattr(logging, os.getenv("LOG_LEVEL_FILE", "INFO").upper(), logging.INFO)

def setup_logging():
    formatter = logging.Formatter("%(asctime)s %(levelname)s\t%(name)s\t%(message)s\t (function %(funcName)s)")

    log = logging.getLogger("sc")
    log.propagate = False
    log.setLevel(min(LOG_LEVEL_CONSOLE, LOG_LEVEL_FILE))

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVEL_CONSOLE)
    console_handler.setFormatter(formatter)
    log.addHandler(console_handler)

    file_handler = logging.FileHandler("sc.log")
    file_handler.setLevel(LOG_LEVEL_FILE)
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)

    root_log = logging.getLogger()
    root_log.setLevel(logging.INFO)
    root_log.addHandler(console_handler)
    root_log.addHandler(file_handler)
