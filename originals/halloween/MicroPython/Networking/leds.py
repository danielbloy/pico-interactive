# This is designed to be used in combination with other modules so has no run(). Simply
# call init() to ensure all messages are registered.

import machine
import random

import uasyncio as asyncio

MAX_DUTY = 65535


class LED:
    def __init__(self, pin, brightness=1.0):
        if brightness < 0 or brightness > 1.0:
            raise Exception("LEDs: Brightness %s is out of range!" % brightness)

        self.pin = pin
        self.pwm = machine.PWM(machine.Pin(pin))
        self.pwm.freq(1000)  # set the frequency of slice 0

        self.set(brightness)

    # Sets the brightness of the LEDs.
    def set(self, brightness):
        if brightness < 0 or brightness > 1.0:
            raise Exception("LEDs: Brightness %s is out of range!" % brightness)

        self.brightness = brightness
        self.pwm.duty_u16(int(MAX_DUTY * brightness))  # set the duty cycle of channel A, range 0-65535

    # Turns the LED fully on.
    def on(self):
        self.set(1.0)

    # Turns the LED fully off.
    def off(self):
        self.set(0)


# This dims and brightens the led. The pulse is controlled with start and step
# which controls the lowest brightness and the speed with which it pulses. The
# led has a range of 0 to 255 to control the brightness.
async def pulse(led, start=50, step=5):
    brightnesses = [ii for ii in range(start, 255, step)]
    brightnesses.extend([ii for ii in range(255, start, -step)])
    for brightness in brightnesses:
        led.set(brightness / 255)
        await asyncio.sleep_ms(50)


# This flickers the led. The flicker sets the brightness to a random value between
# base and (base + flame) using a 0 to 255 range.
async def flicker(led, base=150, flame=105):
    led.set((base + random.randint(0, flame)) / 255)


def init():
    pass

# There is no run() function as this is just designed to be used by other modules.
