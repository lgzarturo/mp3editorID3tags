import datetime
import logging
import logging.handlers as handlers
import os
from pathlib import Path


class Logging:
    def __init__(self, name='main'):
        size_in_megabytes: int = 60 * 1024 * 1024
        backup_files_in_disk: int = 7
        file_content_encoding: str = 'utf-8'
        log = logging.getLogger(name)
        log.setLevel(logging.INFO)
        logger_filename = os.path.join(os.path.join(Path(__file__).parent, 'logs'), f'logging{name}.log')
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s \t[%(filename)s:%(lineno)s - %(name)s:%(funcName)s()] %(message)s'
        )
        file_handler = handlers.RotatingFileHandler(
            logger_filename,
            encoding=file_content_encoding,
            maxBytes=size_in_megabytes,
            backupCount=backup_files_in_disk
        )
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        log.addHandler(file_handler)
        log.addHandler(stream_handler)
        self.log = log

    def get_logger(self):
        return self.log

    def elapsed_time(self, start_time: datetime, message: str = None):
        if message is not None:
            self.log.info(message)
        end_time = datetime.datetime.now()
        time_diff = (end_time - start_time)
        execution_time_in_seconds = time_diff.total_seconds()
        execution_time = execution_time_in_seconds * 1000
        self.log.info("Elapsed time: {:0.2f} ms ~ {:0.2f} seg".format(execution_time, execution_time_in_seconds))
