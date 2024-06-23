# Summary

TODO: Provide details of the expected configuration of the base node.

## Base node

For more details on the design and evolution of the base node hardware, see
the section on [hardware](../hardware/README.md).

Base board configuration (all optionally enabled):

* 1 x button
* 1 x buzzer
* 1 x OLED display (128 x 64)
* 1 x Ultrasonic Sensor
* 1 x Network
* 1 x UART
* 1 x NeoPixel connector (input shared with audio board in reference base board)
* 1 x Audio Board with 2 x ADC inputs (1 shared with NeoPixel connector)
* 1 x Optional custom daughter board

The single button can be used to cycle through the display screens with a short
single press. A long hold of 3 seconds will force a device reboot. A double press
will support a configurable action by the node.

The buzzer is intended to be used to signal errors or checks and not expected to
be the primary audio output method. However, in small boards that are limited for
pins or space and intended to be used indoors only, the buzzer does make an
acceptable *tune*.

The audio board is pluggable to allow for different types of output connector,
amplifier, mono or stereo input, power usage. The sound boards are also stackable
allowing for one sound board to use one input and a second sound board to use
the second input.

The OLED display will have an optional screen per framework module (buzzer, button,
Network, UART, ultrasonic, debug) as well as an off/blank screen. The default screen
will be configurable.

The ultrasonic sensor will be able to return the last distance calculated. It can
also be configured to trigger an event when a set distance is broken. The number
of distance events will be configurable as are the event callbacks.

## Using the pico-interactive library

TODO: Properly flesh this out, explaining the contents of each file.

### Setup on a CircuitPython device

Copy the framework directory onto the CircuitPython device.

### Examples

See `tests/on_device` for examples.

### Configuration

Settings that are designed to be changed to configure behaviour will be found in `config.toml`
and `config.py`. Each device can have different settings. The settings in `control.py` are not
expected to change within the same type of microcontroller (but may have to change across
microcontroller types).

