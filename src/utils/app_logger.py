import logging

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

class AppLogger:

    @staticmethod
    def info(name=None):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(LOG_FORMAT)

        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        return logger

    @staticmethod
    def error(name=None):
        logger = logging.getLogger(name)
        logger.setLevel(logging.ERROR)

        formatter = logging.Formatter(LOG_FORMAT)

        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        return logger
