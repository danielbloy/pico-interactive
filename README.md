# pico-interactive

Please see my website [Code Club Adventures](http://codeclubadventures.com/) for more coding materials.

## Inspiration

For details of the inspiration of this project, see
[pico-interactive-originals](https://github.com/danielbloy/pico-interactive-origins)

### Halloween 2024

The first interactive display to make use of this project will be Halloween 2024.
For more information on that project, see
[pico-interactive-halloween](https://github.com/danielbloy/pico-interactive-halloween).

## Overview

This project brings together the ideas behind three projects created in 2023 into
a single common (easily extensible) framework that can be used with a range of
CircuitPython boards (though originally designed
for [Raspberry Pi Pico](https://thepihut.com/products/raspberry-pi-pico-w?variant=41952994787523)).
The framework is designed to be used for single board projects used in Coding Clubs
up to larger interactive display installations that consist of many boards each
performing in isolation or coordinated over network connections. The framework has
been tested and works with a range of microcontroller boards. See the
[README.md](circuitpython/README.md) in the `circuitpython` directory for a full
list of supported boards and CircuitPython versions.

The basic structure of this project is:

* `circuitpython` contains the exact builds of CircuitPython that have been tested
  with this project along with the libraries that are used extracted out into the
  `circuitpython/lib` directory.
* `demo` contains demonstration and test *interactive* displays that are used to test
  the functionality of this project on a range of boards.
* `docs` contains the documentation for the `interactive` and `coordinator` directories.
* `hardware` contains information on the boards that have been designed for use with
  this framework and interactive displays.
* `interactive` contains the base framework code which provides the basic functionality
  that operates on a supported board. This code is configurable and extensible, allowing
  the individual nodes in an interactive display to use whichever functionality they
  need, whilst also providing their own customisation code. All nodes will make use
  of the `interactive` framework.
* `tests` contains the tests for the code contained in the `interactive` directory as
  well as `on_device` tests that can be used to verify against a particular hardware
  device.

All work in this project are provided under a permissive license to allow this code to
be used in a range of educational and personal settings. See the end of this readme for
more information about the license.

## List of functionality

* [x] Add generic task runner that handles both completion and exceptions and support restarts.
  * [x] Works on CircuitPython
  * [x] Works with Blinka
* [x] Add support for logging in both Desktop and Pico environments.
  * [x] Works on CircuitPython
  * [x] Works with Blinka
* [x] Add button support for single, double and long-presses.
  * [x] Works on CircuitPython
  * [x] Works with Blinka
* [x] Add buzzer support for playing tones.
  * [x] Works on CircuitPython
  * [x] Works with Blinka
* [x] Migrate music.py/Song from originals/christmas to buzzer.py as Melody
  * [ ] Write tests
* [x] Migrate music.py/SongSequence from originals/christmas to buzzer.py as MelodySequence
  * [ ] Write tests
* [x] Add NeoPixel support
  * [x] Works on CircuitPython
  * [x] Works with Blinka
* [x] Migrate Flicker from originals/christmas and originals/light_jars to pixel.py
  * [ ] Add tests for Flicker
* [ ] Add a Flame effect for pixels
  * [ ] Add tests for Flame
* [ ] Add a Lightning effect for pixels
  * [ ] Add tests for Lightning
* [x] Add LED support
  * [x] Works on CircuitPython
  * [x] Works with Blinka
* [x] Add Ultrasonic sensor support
  * [x] Works on CircuitPython
  * [ ] ~~Works with Blinka~~ Blinka is too slow on PC
* [x] Add Audio support
  * [x] Works on CircuitPython
  * [ ] ~~Works with Blinka~~ Blinka is too slow on PC
* [x] Add Wi-Fi support
  * [x] Works on CircuitPython
  * [x] Works with Blinka
* [x] Add support for network node information page: index, inspect, cpu-information
* [x] Add support for standard messages: alive, name, role, blink, led on/off, restart, trigger
* [x] Add support for network directory via coordinator node (PC/Raspberry Pi) (register/unregister, heartbeat etc.)
* [ ] Add current time of day support via Wi-Fi
  * [ ] Works on CircuitPython
  * [ ] Works with Blinka
* [ ] Trigger message should accept JSON data.
* [ ] Add in a directory-information route to export as JSON data about the directory.
* [ ] Improve the '/' and '/inspect' routes with more information and better formatting.
* [ ] Add in a node-information route to return the node information as JSON.
* [ ] Migrate to a lighterweight, faster and async HTTP server stack such
  as [Biplane](https://github.com/Uberi/biplane).
* [ ] Add Servo support
  * [ ] Works on CircuitPython
  * [ ] Works with Blinka
* [ ] Add Motor support
  * [ ] Works on CircuitPython
  * [ ] Works with Blinka
* [ ] Add UART support
  * [ ] Works on CircuitPython
  * [ ] Works with Blinka
* [ ] Add I2S audio support
  * [ ] Works on CircuitPython
  * [ ] Works with Blinka
* [ ] Add DFPlayer Pro audio support
  * [ ] Works on CircuitPython
  * [ ] Works with Blinka
* [ ] Add OLED/TFT screen support
  * [ ] Works on CircuitPython
  * [ ] Works with Blinka
* [ ] Embed pico-interactive version number in library based on release.
* [ ] Make a pico-interactive release (
  see [Creating and sharing a CircuitPython library](https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library?view=all#mpy-2982472-11)):
  * [ ] Compile to`.mpy` files

## Setting up the development environment

This project has been developed using the PyCharm IDE with a VENV for bythong as well
as using Blnika (see [Blinka](#blinka)) to easily test the interaction with a
CircuitPython board. The other libraries that are used and need to be installed into
the Virtual Environment are:

* `pytest` (see [pytest](https://docs.pytest.org/en/8.2.x/) for more information)

## Blinka

Use the Adafruit resources at [CircuitPython Libraries on any Computer with Raspberry Pi Pico](
https://learn.adafruit.com/circuitpython-libraries-on-any-computer-with-raspberry-pi-pico/overview)
to setup Blinka. Once setup it'll make it much easier to test CircuitPython code and will be an
invaluable tool when building your own CircuitPython software. Once Blinka is setup, it is trivial
to then run CircuitPython programs directly from within [PyCharm IDE](https://www.jetbrains.com/pycharm/).

Once Blinka is setup and you are running your CircuitPython code from PyCharm, you will need to
add the appropriate libraries into your `venv`. In the project covered here it includes:

```shell
adafruit-circuitpython-busdevice
adafruit-circuitpython-connectionmanager
adafruit-circuitpython-debouncer
adafruit-circuitpython-hcsr04
adafruit-circuitpython-httpserver
adafruit-circuitpython-led-animation
adafruit-circuitpython-logging
adafruit-circuitpython-neopixel
adafruit-circuitpython-pixelbuf
adafruit-circuitpython-requests
adafruit-circuitpython-ticks
adafruit-circuitpython-typing
```

Beware that there are some limitations with Blinka that means it cannot be used to test
everything. All of your application code will still need to be tested on the device that
you want to run on to make sure it works in that environment. So far, the main issues
that I have found with Blinka are:

* It is significantly slower that running on the device itself. This is not because your
  computer is slow, it's because of the overhead of calculating and transferring data to
  and from the device. Running your application code on the device is always much faster.
* More than one strand of Neopixels will not work properly. If you are running a single
  strand of Neopixels then Blinka works absolutely fine (although it is slower to update than
  running on the device). If however you run multiple strands from different pins then What
  seems to happen is they get combined and output on a single strand. Running your code
  on the device will work fine though (this was infuriating when building the skull path
  nodes).
* Ultrasonic sensors do not give good results. This is possibly related to the speed issue
  but when testing Ultrasonic sensors, I did not get anything like sensible or consistent
  values. Running on the device worked fine though.
* Audio support seems to be unavailable as I was unable to find the appropriate library to
  add to the virtual environment. I did not invest much time into solving this issue as
  the audio is largely handled by CircuitPython and the pico-interactive code is little
  more than a thin layer around it.

## License

All materials provided in this project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0
International License. To view a copy of this license, visit
<https://creativecommons.org/licenses/by-nc-sa/4.0/>.

In summary, this means that you are free to:

* **Share** — copy and redistribute the material in any medium or format.
* **Adapt** — remix, transform, and build upon the material.

Provided you follow these terms:

* **Attribution** — You must give appropriate credit , provide a link to the license, and indicate if changes were made.
  You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
* **NonCommercial** — You may not use the material for commercial purposes.
* **ShareAlike** — If you remix, transform, or build upon the material, you must distribute your contributions under the
  same license as the original.
