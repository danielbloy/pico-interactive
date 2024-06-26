# This file sets up some variables that are determined from the environment
# that the code is being executed in to allow various parts of the program
# to selectively run based on what is available to it.
#
# THIS FILE SHOULD NOT IMPORT ANY OTHER FILE IN THE FRAMEWORK
#
import os

__is_blinka_available: bool = False
__is_running_on_microcontroller: bool = True

try:
    # If this works, we assume this means that we have access to pins either
    # through Blinka on a Desktop or because we are running on a microcontroller.
    import board

    __is_blinka_available = True

except ImportError:
    __is_blinka_available = False

try:
    # Here we use the environment variable to determine if we are running on a
    # Microcontroller or not.
    __is_running_on_microcontroller = os.getenv("BLINKA_U2IF") != "1"

    # If we are running on a microcontroller, we force Blinka off as we are
    # not expecting to run Blinka on a microcontroller
    if __is_running_on_microcontroller:
        __is_blinka_available = False

except AttributeError:
    pass

# Override for when running under a CI system.
__is_running_in_ci: bool = (
        os.getenv("CI") is not None or
        os.getenv("TRAVIS") is not None or
        os.getenv("CIRCLECI") is not None or
        os.getenv("GITLAB_CI") is not None or
        os.getenv("GITHUB_ACTIONS") is not None or
        os.getenv("GITHUB_RUN_ID") is not None)

if __is_running_in_ci:
    __is_running_in_in_ci = True
    __is_running_on_microcontroller = False
    __is_blinka_available = False


def is_running_in_ci() -> bool:
    """
    Returns whether the code is running in the CI system (GitHub actions).
    When running in CI, the environment is forced to Desktop without pins.
    """
    return __is_running_in_ci


def is_running_on_microcontroller() -> bool:
    """
    Returns whether the code is running on a microcontroller or not.
    """
    return __is_running_on_microcontroller


def is_running_on_desktop() -> bool:
    """
    Returns whether the code is running on a desktop or not.
    """
    return not __is_running_on_microcontroller


def is_blinka_available() -> bool:
    """
    Returns whether Blinka is available or not. This will always be false when
    running on a microcontroller.
    """
    return __is_blinka_available


def are_pins_available() -> bool:
    """
    Returns whether pins are available or not. This will be true when the code is
    running in one of the following environment:
    * On an actual microcontroller.
    * On a desktop with Blinka available.
    """
    return __is_blinka_available or __is_running_on_microcontroller


def report():
    """
    Produces a simple report of the environment the code is running in.
    """
    if is_running_in_ci():
        print("Running on CI")

    running_on = "microcontroller" if is_running_on_microcontroller() else "desktop"
    pins_available = "are" if are_pins_available() else "are not"

    print(f'Running on a {running_on}. Pins {pins_available} available.')
