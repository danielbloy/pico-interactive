# This is a very thin layer over the top of Python and CircuitPython logging.
# It offers a very basic set of functions using the single fallback logger.
# This is for simplicity as we are expecting this to run on a microcontroller
# where complex logging is simply not available.
from framework.environment import is_running_on_desktop

if is_running_on_desktop():
    import logging
    from logging import CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET

    FORMAT = '%(asctime)s %(message)s'
    logging.basicConfig(format=FORMAT, level=WARNING)

else:
    import adafruit_logging as logging
    from adafruit_logging import CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET

logger = logging.getLogger(__name__)

# Prevents PyCharm from clearing up the unused imports.
__CRITICAL = CRITICAL
__ERROR = ERROR
__WARNING = WARNING
__INFO = INFO
__DEBUG = DEBUG
__NOTSET = NOTSET


def set_log_level(level) -> None:
    """
    Sets the logging level to use in the same way as Logging. Defaults to WARNING.

    :param level: A number, usually oOne of CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
    """
    logger.setLevel(level)


def stacktrace(e: Exception) -> None:
    """
    Puts a stacktrace out for the exception using the DEBUG log level.

    :param e: The exception whose stack trace we want to log.
    """
    import traceback
    if is_running_on_desktop():
        # This is to support Python 3.9 as well as Python 3.12.
        for s in traceback.format_exception(e, value=None, tb=None):
            logger.debug(s)
    else:
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


def critical(message: str) -> None:
    """Writes message at the CRITICAL log level."""
    logger.critical(message)
