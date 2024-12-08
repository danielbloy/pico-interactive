## Roadmap

Below you will find the proposed roadmap of functionality that I am planning to build into
the `pico-interactive``project. This is all subject to change as project priorities may
require different functionality sooner. No timelines are provided, but I ideally want to have
most of this done before end March 2025 to give me plenty of time to work on the network
code rewrite before building the new hardware for Halloween 2025.

Throughout all releases work will continue to add the additional test support that was missing
from the libraries that were migrated but had no tests.

## Version 1.0.2

* Validate support for CircuitPython 9.2.x and Pico 2 boards.
* Update to newest CircuitPython library bundle.
* Document the best way to use `pico-interactive` based on available device RAM/board classification
  (i.e. Network uses so much RAM that it is difficult for a Pico 1 to do much else).
* Include version number in the `pico-interactive` library.

## Version 1.0.3

* Remove most of the existing content of the `hardware` section, moving it to the `Halloween` repository.
* Add a section for each explicitly supported board in the `hardware` with examples to make it as
  simple as possible for newcomers to get up and running with off the shelf hardware.
* Add a section for the "Christmas Board" -> "Demo Board" as an example of a trivial homemade board.
* Remove the `demo` section, placing the example under `boards/demo_board`.

## Version 1.0.4

* Move the `tests/on_device` section to `examples` and provide some documentation on how to run on different devices.
* Start writing the `docs` section along with documentation roadmap.
* Investigate optimising task creation to remove unnecessary nested tasks; hopefully to remove memory footprint.

## Version 1.0.5

* Add full support hardware test cycle for Pi Zero 2, Pi 3A/3A, Pi 400/4B boards, including setup documentation.

## Version 1.0.6

* Add support for Servos required for the Inventor/Lego Car projects for Code Club.

## Version 1.0.7

* Add support for communications between Picos using UART and possible 1-wire support.
* Examples should include some using 3.5mm jack breakouts to connect devices.

## Version 1.0.8

* Add I2S audio support in addition to the existing PWM.

## Version 1.0.9

* Add motor support.

## Version 1.0.10

* Add DFPlayer support.

## Version 1.0.11

* Compile to `.mpy` files and add an official release process.

## Version 1.1.0

* Migrate to a lighter weight, faster and async HTTP server stack such as [Biplane](https://github.com/Uberi/biplane).
  This will likely involve a notable reworking of the network code.
* Add time of day support.
* Support JSON in messages.