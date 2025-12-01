import logging
import sys

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

class AppLogger:

    @staticmethod
    def info(name=None):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            ch = logging.StreamHandler(sys.stdout)
            ch.setFormatter(logging.Formatter(LOG_FORMAT))
            logger.addHandler(ch)
            logger.propagate = False  # отключаем логирование выше по иерархии

        return logger

    @staticmethod
    def error(name=None):
        logger = logging.getLogger(name)
        logger.setLevel(logging.ERROR)

        if not logger.handlers:
            ch = logging.StreamHandler(sys.stderr)
            ch.setFormatter(logging.Formatter(LOG_FORMAT))
            logger.addHandler(ch)
            logger.propagate = False  # отключаем логгирование выше по иерархии

        return logger
