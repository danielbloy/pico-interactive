## Roadmap

Below you will find the proposed roadmap of functionality that I am planning to build into
the `pico-interactive``project. This is all subject to change as project priorities may
require different functionality sooner. No timelines are provided, but I ideally want to have
most of this done before end March 2025 to give me plenty of time to work on the network
code rewrite before building the new hardware for Halloween 2025.

Throughout all releases work will continue to add the additional test support that was missing
from the libraries that were migrated but had no tests.

## Version 2.0.0

**Structural Changes**

* Remove the adafruit_animations from the polyfills. These can be imported directly and it will
  help simplify the code. The polyfills are really only needed for the core framework code and
  the animations aren't. Due to this being a breaking change, I will be bumping up to the next
  major version.
* Migrate to a lighter weight, faster and async HTTP server stack such as [Biplane](https://github.com/Uberi/biplane).
  This will likely involve a notable reworking of the network code.

**Testing and Documentation Improvements**

* Modify the `test/on_device` programs to use configuration to make testing multiple devices easier.
* Add instructions on each `test/on_device` program to make it easier to know what to expect.
* Move the `tests/on_device` section to `examples` and provide some documentation on how to run on
  different devices.
* Have a "test all" program that works within Pico 1 memory limits and one that works with Pico 2.
* Ensure device tests can run with Blinka too.

**Hardware Support**

* Remove most of the existing content of the `hardware` section, moving it to the `Halloween` repository.
* Add a section for each explicitly supported board in the `hardware` with examples to make it as
  simple as possible for newcomers to get up and running with off the shelf hardware.
* Add a section for the "Christmas Board" -> "Demo Board" as an example of a trivial homemade board.
* Remove the `demo` section, placing the example under `boards/demo_board`.
* Document the best way to use `pico-interactive` based on available device RAM/board classification
  (i.e. Network uses so much RAM that it is difficult for a Pico 1 to do much else).
* Add full support hardware test cycle for Pi Zero 2, Pi 3A/3A, Pi 400/4B boards, including setup documentation.

**Simplification and Optimisation**

* Investigate optimising task creation to remove unnecessary nested tasks; hopefully to remove memory
  footprint.
* Look to simplify the framework further to make it easier to use.

**Enhancements and Bug Fixes**

* Fix issue with `5_validate_interactive.py` defaulting to using an Ultrasonic sensor on demo board.
* Include version number in the `pico-interactive` library.
* Support using board.LED for an LED in tests (so it works with Pico 2 W)
* Add time of day support.
* Support JSON in messages.

## Version 2.0.1

* Add support for communications between Picos using UART and possible 1-wire support.
* Examples should include some using 3.5mm jack breakouts to connect devices.

## Version 2.0.2

* Examples with support for Servos required for the Inventor/Lego Car projects for Code Club.

## Version 2.0.3

* Examples with I2S audio support in addition to the existing PWM.

## Version 2.0.4

* Examples with motor support.

## Version 2.0.5

* Examples with DFPlayer support.

## Version 2.1.0

* Compile to `.mpy` files and add an official release process.

