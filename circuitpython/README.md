# CircuitPython

This directory contains a copy of all the CircuitPython images and libraries that
this project is tested against and supports. Currently, the project is being built
against:

## Tested CircuitPython versions

The following table illustrates the versions of CircuitPython that have been tested
with `pico-interactive`. This is not meant to be an exhaustive list so the absence
of an indicator does not mean that it doesn't work - just that it has not been tested.
As newer versions of CircuitPython support are validated, the older versions will stop
being tested.

| CircuitPython Version:  | 9.2.1 | 9.1.4 | 9.0.5 |
|-------------------------|-------|-------|-------|
| pico-interactive v1.0.0 |       | Pass  | Pass  |
| pico-interactive v1.0.1 | Pass  | Pass  | Pass  |

## Tested Microcontrollers 

Even though this framework was initially designed for my projects based on Raspberry
Pi Pico boards, the only real restriction is whether a particular microcontroller has
a supported CircuitPython distribution or not. Almost all of my testing is done on
Raspberry Pi Pico boards though I do also have some Adafruit M4 based microcontrollers
that I will be testing at some point in the future. As well as CircuitPython support,
any microcontrollers that want to run `pico-insteractive` should come with plenty of
RAM. This almost certainly means anything with less than 100Kb of RAM is going to
struggle.

There are masses of microcontroller boards and variations. The following list are those
that I own and test or use with my projects.

Microcontroller boards tested with CircuitPython 9.2.x and `pico-interactive`:

* [Raspberry Pi Pico (no wifi support)](https://shop.pimoroni.com/products/raspberry-pi-pico?variant=40059364311123)
* [Raspberry Pi Pico W](https://shop.pimoroni.com/products/raspberry-pi-pico-w?variant=40059369652307)
* [Pimoroni Plasma Stick 2040 W](https://shop.pimoroni.com/products/plasma-stick-2040-w?variant=40359072301139)
* [Pimoroni Tiny 2040 (no wifi support)](https://shop.pimoroni.com/products/tiny-2040?variant=39560012234835)
* [Pimoroni Inventor 2040 W](https://shop.pimoroni.com/products/inventor-2040-w?variant=40053063155795)
* [Pimoroni Pico W Unicorn (Stellar, Galactic or Cosmic)](https://shop.pimoroni.com/products/space-unicorns?variant=40842033561683)
* [Pimoroni PicoSystem (no wifi support)](https://shop.pimoroni.com/products/picosystem?variant=32369546985555)
* [Raspberry Pi Pico 2 (no wifi support)](https://shop.pimoroni.com/products/raspberry-pi-pico-2?variant=42096955424851)
* [Raspberry Pi Pico 2 W](https://shop.pimoroni.com/products/raspberry-pi-pico-2-w?variant=54852252991867)
* [Pimoroni Plasma 2350](https://shop.pimoroni.com/products/plasma-2350?variant=42092628246611)
* [Pimoroni Tiny 2350 (no wifi support)](https://shop.pimoroni.com/products/tiny-2350?variant=42092638699603)
* [Pimoroni Pico Plus 2 (no wifi support)](https://shop.pimoroni.com/products/pimoroni-pico-plus-2?variant=42092668289107)
* [Pimoroni Pico Plus 2 W](https://shop.pimoroni.com/products/pimoroni-pico-plus-2-w?variant=42182811942995)
* [Adafruit ItsyBitsy M4 Express](https://shop.pimoroni.com/products/adafruit-itsybitsy-m4-express-featuring-atsamd51?variant=12519303086163) 
* [Adafruit EdgeBadge](https://shop.pimoroni.com/products/adafruit-edgebadge-tensorflow-lite-for-microcontrollers?variant=31251813400659)
* [Adafruit PyBadge LC](https://shop.pimoroni.com/products/adafruit-pybadge-lc-makecode-arcade-circuitpython-or-arduino-low-cost-version?variant=30267341111379)
* [BBC micro:bit V2](https://shop.pimoroni.com/products/new-micro-bit-v2?variant=32271548481619)
  * The BBC micro:bit requires updated firmware which you can get from [here](https://microbit.org/get-started/user-guide/firmware/).  
* [KittenBot Meowbit](https://www.kittenbot.cc/products/meowbit-codable-console-for-microsoft-makecode-arcade)

## Supported computers

The `pico-interactive` framework will run on all Desktop PCs running a recent version of Python (
3.10, 3.11 and 3.12 have been tested). Beware of the limitations on pin performance when using Blinka
for pin support on Windows or Linux PCs. There are no such performance limitations on Raspberry Pi SBCs.

* Windows (pins available via Blinka)
* Linux (ins available via Blinka)
* [Raspberry Pi 3A+ (pins via Blinka)](https://shop.pimoroni.com/products/raspberry-pi-3-a-plus?variant=17989206507603)
* [Raspberry Pi Zero 2 W (pins via Blinka)](https://shop.pimoroni.com/products/raspberry-pi-zero-2-w?variant=42101934587987)
