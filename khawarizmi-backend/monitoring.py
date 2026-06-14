# monitoring.py
# Khawarizmi Pro — Sentry + logging

import logging

from config import init_sentry


def setup_monitoring() -> None:
    init_sentry()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
    )
