# Summary
This project will be a CircuitPython project that controls 12 jars that contains 2
NeoPixels each to product dancing light patterns. This will use the same techniques 
to control the NeoPixels as those used in the Code Club Christmas 2023 project.

The NeoPixel jars are in two strands which allows for lots of different arrangements
of the jars. There could be:
* 2 rows with each strand connected in parallel.
* 2 circles with one strand clockwise and the other anti-clockwise.
* 1 x single strand arranged in a line, circle or grid.

The project needs to be able to control the number and orientation of the pixels.

# Hardware
1 x Pimoroni Plasma Stick 2040 (Pi Pico) running Circuit Python.
2 x strands of 6 x Jars, each containing 2 NeoPixels.
1 x reflective sheet to stand the jars on.

# Software
There are two primary modes for the patterns.
* Built-in named modes from the pre-set Animations. 
* Programed named custom modes based on a string of commands. 

As well as hard-coded custom modes, new modes can be sent over the Wi-Fi connection.

The mode (or modes) that are run are selectable over Wi-Fi.

The entry point for all code is `code.py` and configuration is found in `config.py`. 
What code gets executed is dependent on the execution environment. The variables that
control this are in `envrionment.py` and determined based on settings and whether
Blinka is available for import or not. 

The file `pixels.py` contains the code which controls the NeoPixels and can only be
executed when Blinka is available (either on the microcontroller or with a connected
device). similarly, the file `flicker.py` is itself only suitable for `CircuitPython` 
because it inherits from the Adafruit Animation class.

The file `network.py` provides environment relevant networking. If running on a 
microcontroller then it exposes the CircuitPython requests, if not running on a
microcontroller then it exposes the requests module. 

The file `clock.py` provides a clock. It uses the Adafruit IO API to periodically 
fetch the time, which it exposes internally.

The file `events.py` provides eventing facilities based on the clock or other 
scenario.

All sensitive settings such as passwords should be set in `settings.toml` as shown below.
Note, the `settings.toml` file is not stored in source control.
```toml
CIRCUITPY_WIFI_SSID = "wifi-ssid"
CIRCUITPY_WIFI_PASSWORD = "wifi-password"

AIO_USERNAME = "username"
AIO_KEY = "key"
```

# Libraries to install
Python libraries to install
* adafruit-circuitpython-led-animation
* adafruit-circuitpython-neopixel
* adafruit-requests
