# CircuitPython

This directory contains a copy of all the CircuitPython images and libraries that
this project is tested against and supports. Currently, the project is being built
against:

## Supported CircuitPython versions

* [x] CircuitPython 9.0.5
* [ ] CircuitPython 9.1.4 - testing in progress
* [ ] CircuitPython 9.2.0 - testing in progress

The CircuitPython libraries that are required for the project have been extracted
out into the `lib` directory for easy access.

## Supported microcontroller boards

The full set of supported microcontroller boards are:

* [Raspberry Pi Pico (no network support)](https://shop.pimoroni.com/products/raspberry-pi-pico?variant=40059364311123)
* [Raspberry Pi Pico W](https://shop.pimoroni.com/products/raspberry-pi-pico-w?variant=40059369652307)
* [Pimoroni Plasma Stick 2040 W](https://shop.pimoroni.com/products/plasma-stick-2040-w?variant=40359072301139)
* [Pimoroni Tiny 2040 (no network support)](https://shop.pimoroni.com/products/tiny-2040?variant=39560012234835)

The following microcontroller boards are in testing phase for support:

* [Raspberry Pi Pico 2 (no network support)](https://shop.pimoroni.com/products/raspberry-pi-pico-2?variant=42096955424851)
* [Pimoroni Pico Plus 2 (no network support)](https://shop.pimoroni.com/products/pimoroni-pico-plus-2?variant=42092668289107)
* [Pimoroni Pico Plus 2 W](https://shop.pimoroni.com/products/pimoroni-pico-plus-2-w?variant=42182811942995)
* [Pimoroni Plasma 2350](https://shop.pimoroni.com/products/plasma-2350?variant=42092628246611)
* [Pimoroni Tiny 2350 (no network support)](https://shop.pimoroni.com/products/tiny-2350?variant=42092638699603)

### Compatibility matrix

* [x] CircuitPython 9.0.5
  * [x] Raspberry Pi Pico
  * [x] Raspberry Pi Pico W
  * [x] Pimoroni Plasma Stick 2040 W
  * [x] Pimoroni Tiny 2040
* [ ] CircuitPython 9.1.4 - testing in progress
  * [ ] Raspberry Pi Pico
  * [ ] Raspberry Pi Pico W
  * [ ] Pimoroni Plasma Stick 2040 W
  * [ ] Pimoroni Tiny 2040
* [ ] CircuitPython 9.2.0 - testing in progress
  * [ ] Raspberry Pi Pico
  * [ ] Raspberry Pi Pico W
  * [ ] Pimoroni Plasma Stick 2040 W
  * [ ] Pimoroni Tiny 2040
  * [ ] Raspberry Pi Pico 2
  * [ ] Pimoroni Pico Plus 2
  * [ ] Pimoroni Pico Plus 2 W
  * [ ] Pimoroni Plasma 2350
  * [ ] Pimoroni Tiny 2350

## Supported computers

Desktop PCs running (all require Python 3.10 or later; tested with Python 3.10, 3.11 and 3.12):

* Windows (pins available via Blinka, though beware the limitations on pin performance)
* Linux (tested but not with Blinka)
* [Raspberry Pi 3A+ (pins via Blinka)](https://shop.pimoroni.com/products/raspberry-pi-3-a-plus?variant=17989206507603)
* [Raspberry Pi Zero 2 W (pins via Blinka)](https://shop.pimoroni.com/products/raspberry-pi-zero-2-w?variant=42101934587987)

### Compatibility matrix

* [x] Windows
  * [x] Python 3.10
  * [x] Python 3.11
  * [x] Python 3.12
  * [x] Blinka support
* [x] Linux
  * [x] Python 3.10
  * [x] Python 3.11
  * [x] Python 3.12
  * [ ] Blinka support - not tested
* [ ] Raspberry Pi Zero 2 W
  * [ ] Blinka support
* [ ] Raspberry Pi 3A+/3B+
  * [ ] Blinka support
* [ ] Raspberry Pi 4/400
  * [ ] Blinka support
* [ ] Raspberry Pi 5
  * [ ] Blinka support
