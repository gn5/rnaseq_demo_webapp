import logging
from rnaseq_viz.config.config import LOG_LEVEL

LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s'


def setup_logging():
    logging.basicConfig(
        level=logging.getLevelName(LOG_LEVEL),
        format=LOG_FORMAT,
        handlers=[logging.StreamHandler()]
    )
