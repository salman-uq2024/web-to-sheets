import logging
import os
from datetime import datetime


class Logger:
    """Project-wide logger with file and console output."""

    def __init__(self, log_dir: str = 'logs'):
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'{timestamp}.log')
        self.logger = logging.getLogger('web_to_sheets')
        self.logger.propagate = False

        for handler in list(self.logger.handlers):
            self.logger.removeHandler(handler)
            handler.close()

        level = self._resolve_log_level(os.getenv('LOG_LEVEL', 'INFO'))
        self.logger.setLevel(level)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        self.logger.addHandler(console_handler)

    def debug(self, msg: str):
        self.logger.debug(msg)

    def info(self, msg: str):
        self.logger.info(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    @staticmethod
    def _resolve_log_level(level_name: str) -> int:
        try:
            return getattr(logging, level_name.upper())
        except AttributeError:
            return logging.INFO
