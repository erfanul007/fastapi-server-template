import logging
import time
from pathlib import Path

from .config import settings

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / f"{time.strftime('%Y%m%d-%H%M%S')}.log"

LOG_FORMAT = "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"


def setup_logging():
    level = logging.DEBUG if settings.environment == "development" else logging.WARNING
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
        ],
    )
