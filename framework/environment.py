# This file sets up some variables that are determined from the environment
# that the code is being executed in to allow various parts of the program
# to selectively run based on what is available to it.
import os

# TODO: Rework this file so that it is more pythonic (and integrates with the logging framework).

isBlinkaAvailable: bool = False
try:
    import board

    isBlinkaAvailable = True
except:
    isBlinkaAvailable = False

print(f"Blinka available: {isBlinkaAvailable}")

isRunningOnMicroController: bool = True
try:
    isRunningOnMicroController = os.environ["BLINKA_U2IF"] != "1"

except:
    pass

print(f"Running on a microcontroller: {isRunningOnMicroController}")
