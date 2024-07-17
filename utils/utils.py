import re

import logging

from .config import log_level

logger = logging.getLogger(__name__)
logger.setLevel(log_level)


def check_email(email):
    pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(pattern.match(email))
