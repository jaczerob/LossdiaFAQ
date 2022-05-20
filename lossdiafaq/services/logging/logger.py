import logging
import sys

from loguru import logger


logger.remove()


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)


def log_formatter(record) -> str:
    fmt = "<green>{time:YYYY-MM-DD HH:mm:ss}</> | <level>{level: <8}</> | <cyan>{name}:{function}:{line}</> - {message}\n"

    if record["exception"]:
        fmt += "{exception}\n"

    return fmt


def file_log_formatter(record):
    fmt = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n"

    if record["exception"]:
        fmt += "{exception}\n"

    return fmt


logger.add(sys.stderr, format=log_formatter, backtrace=True, diagnose=True, level="INFO")
logger.add("logs/file_{time}.log", format=file_log_formatter, backtrace=True, diagnose=True, rotation="50 MB")
