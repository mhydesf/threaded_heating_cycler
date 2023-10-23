import os
import logging
import datetime
from typing import Optional
from logging import Logger, LogRecord, handlers
from config.recursive_namespace import RecursiveNamespace


class MyFormatter(logging.Formatter):
    converter = datetime.datetime.fromtimestamp

    def formatTime(
        self,
        record: LogRecord,
        datefmt: Optional[str]=None
    ) -> str:
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            s = ct.strftime("%Y-%m-%dT%H:%M:%S,%f")
        return s


class LoggerManager:
    logger = None
    name = "log"

    def __init__(self) -> None:
        raise Exception("{} is class only".format(self.__class__.__name__))

    @classmethod
    def get_logger(
        cls,
        config: RecursiveNamespace,
        log_only=False
    ) -> Logger:
        if cls.logger is not None:
            return cls.logger
        config.log_only = log_only
        config.path = cls.get_path(config)
        cls.logger = cls._create_logger(config)
        return cls.logger

    @classmethod
    def get_path(
        cls,
        config: RecursiveNamespace,
    ) -> str:
        if not os.path.isdir(config.directory):
            os.makedirs(config.directory)

        file_name = config.file_name.format(
            name=config.name, date=datetime.datetime.now())
        path = os.path.join(config.directory, file_name)
        return path

    @staticmethod
    def _create_logger(config: RecursiveNamespace) -> Logger:
        name = config.name
        level = config.level
        format = config.format
        suffix = config.suffix
        log_only = config.log_only
        path = config.path

        logger = logging.getLogger(name)
        logger.setLevel(level)

        formatter = MyFormatter(format)

        rotate_handle = handlers.TimedRotatingFileHandler(
            path,
            when="midnight", interval=1
        )
        rotate_handle.setLevel(level)
        rotate_handle.setFormatter(formatter)
        rotate_handle.suffix = suffix
        logger.addHandler(rotate_handle)

        if not log_only:
            print_handle = logging.StreamHandler()
            print_handle.setLevel(level)
            print_handle.setFormatter(formatter)
            logger.addHandler(print_handle)

        return logger

