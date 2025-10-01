import logging
import os
from datetime import datetime


class Logger:
    def __init__(self, log_dir='logs'):
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        self.logger = logging.getLogger('web_to_sheets')
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        # Ensure we do not accumulate handlers across instantiations when reusing this logger
        for handler in list(self.logger.handlers):
            self.logger.removeHandler(handler)
            handler.close()

        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def info(self, msg):
        self.logger.info(msg)

    def error(self, msg):
        self.logger.error(msg)
