# This file sets up some variables that are determined from the environment
# that the code is being executed in to allow various parts of the program
# to selectively run based on what is available to it.
#
# THIS FILE SHOULD NOT IMPORT ANY OTHER FILE IN THE FRAMEWORK
#
import os
import sys

################################################################################
# P L A T F O R M
################################################################################
# Internal properties to determine which platform we are running on.
__is_running_on_microcontroller: bool = False
__is_running_on_linux: bool = False
__is_running_on_mac: bool = False
__is_running_on_windows: bool = False

# First, check the target environment. This is the recommended way to check for
# CircuitPython (see https://docs.circuitpython.org/en/latest/docs/library/sys.html#sys.implementation)
if sys.implementation == "circuitpython":
    __is_running_on_microcontroller = True
else:
    # We are not running on CircuitPython so we can assume we are running on
    # a desktop type environment (Windows, Linux or Mac).
    __is_running_on_linux = sys.platform == "linux" or sys.platform == "linux2"
    __is_running_on_mac = sys.platform == "darwin"
    __is_running_on_windows = sys.platform == "win32"

################################################################################
# P I N S
################################################################################
# Internal properties to determine if we have access to Pins.
__are_pins_available: bool = __is_running_on_microcontroller

# If we are not running in an environment where we already know we have
# pins available (typically a Desktop) then lets see what we have access to.
#
# NOTE: We cannot simply try and import adafruit_blinka and check for that as
#       we make use of blinka even when pins are not available. Therefore we
#       check to for the environment variable that determines if a blinka
#       device is available first
if not __are_pins_available and os.getenv("BLINKA_U2IF") == "1":

    try:
        # If this works, we assume this means that we have access to pins either
        # through Blinka on a Desktop or because we are running on a microcontroller.
        import board

        __are_pins_available = True

    except ImportError:
        __are_pins_available = False

################################################################################
# C I    S Y S T E M
################################################################################
__is_running_in_ci: bool = False
__is_running_under_test: bool = False

# Only perform these checks if we are not running on a microcontroller.
if not __is_running_on_microcontroller:
    __is_running_under_test = 'unittest' in sys.modules.keys()

    # Override for when running under a CI system.
    __is_running_in_ci = (
            os.getenv("CI") is not None or
            os.getenv("TRAVIS") is not None or
            os.getenv("CIRCLECI") is not None or
            os.getenv("GITLAB_CI") is not None or
            os.getenv("GITHUB_ACTIONS") is not None or
            os.getenv("GITHUB_RUN_ID") is not None)

    if __is_running_in_ci:
        __is_running_in_in_ci = True
        __is_running_on_linux = True

        # Turn everything else off.
        __is_running_on_microcontroller = False
        __is_running_on_mac = False
        __is_running_on_windows = False
        __are_pins_available = False


def is_running_in_ci() -> bool:
    """
    Returns whether the code is running in the CI system (GitHub actions).
    When running in CI, the environment is forced to Desktop without pins.
    """
    return __is_running_in_ci


def is_running_under_test() -> bool:
    """
    Returns whether the code is running under test. This will always be true
    when running in the CI system.
    """
    return is_running_in_ci() or __is_running_under_test


def is_running_on_microcontroller() -> bool:
    """
    Returns whether the code is running on a microcontroller or not.
    """
    return __is_running_on_microcontroller


def is_running_on_desktop() -> bool:
    """
    Returns whether the code is running on a desktop (Windows, Linux or
    Mac) or not.
    """
    return not __is_running_on_microcontroller


def are_pins_available() -> bool:
    """
    Returns whether pins are available or not. This will be true when the code is
    running in one of the following environment:
    * On an actual microcontroller.
    * On a desktop with Blinka or equivalent available.
    """
    return __are_pins_available


def report():
    """
    Produces a simple report of the environment the code is running in.
    """
    if is_running_in_ci():
        print("Running in CI")

    running_on = "microcontroller" if is_running_on_microcontroller() else sys.platform
    pins_available = "are" if are_pins_available() else "are not"

    print(f'Running on {running_on}. Pins {pins_available} available.')
