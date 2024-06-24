# This is a very thin layer over the top of Python and CircuitPython logging.
# It offers a very basic set of functions using the single fallback logger.
# This is for simplicity as we are expecting this to run on a microcontroller
# where complex logging is simply not available.
from framework.environment import is_running_on_desktop

if is_running_on_desktop():
    import logging

else:
    import adafruit_logging as logging

from logging import CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET

# Prevents PyCharm from clearing up the unused imports.
__CRITICAL = CRITICAL
__ERROR = ERROR
__WARNING = WARNING
__INFO = INFO
__DEBUG = DEBUG
__NOTSET = NOTSET

logger = logging.getLogger(__name__)
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT, level=WARNING)


def set_log_level(level) -> None:
    """
    Sets the logging level to use in the same way as Logging. Defaults to WARNING.

    :param level: A number, usually oOne of CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
    """
    logging.basicConfig(level=level)


def stacktrace(e: Exception) -> None:
    """
    Puts a stacktrace out for the exception using the DEBUG log level.

    :param e: The exception whose stack trace we want to log.
    """
    import traceback
    for s in traceback.format_exception(e):
        logger.debug(s)


def debug(message: str) -> None:
    """Writes message at the DEBUG log level."""
    logger.debug(message)


def info(message: str) -> None:
    """Writes message at the INFO log level."""
    logger.info(message)


def warn(message: str) -> None:
    """Writes message at the WARNING log level."""
    logger.warning(message)


def error(message: str) -> None:
    """Writes message at the ERROR log level."""
    logger.error(message)


def exception(message: str) -> None:
    """Writes message at the ERROR log level with a stacktrace."""
    logger.exception(message)


def critical(message: str) -> None:
    """Writes message at the CRITICAL log level."""
    logger.critical(message)
