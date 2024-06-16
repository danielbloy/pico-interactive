# Python logging:
# https://realpython.com/python-logging/
# https://docs.python.org/3/library/logging.html
#
# CircuitPython logging:
# https://docs.circuitpython.org/projects/logging/en/latest/api.html


def stacktrace(exception: Exception) -> None:
    import traceback
    print(traceback.format_exception(exception))


# TODO: this should be re-routed to a suitable logging framework based on the execution environment.
def debug(message: str) -> None:
    print(message)


def info(message: str) -> None:
    print(message)


def warn(message: str) -> None:
    print(message)


def error(message: str) -> None:
    print(message)


def critical(message: str) -> None:
    print(message)
