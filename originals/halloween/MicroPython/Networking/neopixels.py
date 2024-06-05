# This is designed to be used in combination with other modules so has no run(). Simply
# call init() to ensure all messages are registered.

import random, array
from machine import Pin
import rp2

import uasyncio as asyncio


############################################
# RP2040 PIO and Pin Configurations
############################################
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT,
             autopull=True, pull_thresh=24)  # PIO configuration
# define WS2812 parameters
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1).side(0)[T3 - 1]
    jmp(not_x, "do_zero").side(1)[T1 - 1]
    jmp("bitloop").side(1)[T2 - 1]
    label("do_zero")
    nop().side(0)[T2 - 1]
    wrap()


# RGB Colours
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PURPLE = (180, 0, 255)
ORANGE = (255, 30, 0)
WHITE = (255, 255, 255)
OFF = (0, 0, 0)


class NeoPixels:
    def __init__(self, pin, count, brightness=1.0):
        if count < 1:
            raise Exception("NeoPixels: At least 1 pixel is required!")

        if brightness < 0 or brightness > 1.0:
            raise Exception("NeoPixels: Brightness %s is out of range!" % brightness)

        self.pin = pin
        self.count = count
        self.brightness = brightness

        # Create the StateMachine with the ws2812 program, outputting on pre-defined pin
        # at the 8MHz frequency
        self.sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(pin))

        # Activate the state machine
        self.sm.active(1)

        self.red = array.array("I", [0 for _ in range(count)])
        self.green = array.array("I", [0 for _ in range(count)])
        self.blue = array.array("I", [0 for _ in range(count)])
        self.bright = array.array("d", [1.0 for _ in range(count)])

    # Sets the individual pixel i (zero indexed) to colour. The brightness parameter is a relative
    # percentage of the brightness that the NeoPixels were initialised with. The change will not be
    # visible in the NeoPixels until update() is called.
    def set(self, i, colour, brightness=1.0):
        if i < 0 or i >= self.count:
            raise Exception("NeoPixels: Index %s is out of bounds!" % i)

        if brightness < 0 or brightness > 1.0:
            raise Exception("NeoPixels: Brightness %s is out of range!" % brightness)

        self.red[i] = colour[0] & 0xFF
        self.green[i] = colour[1] & 0xFF
        self.blue[i] = colour[2] & 0xFF
        self.bright[i] = brightness

    # Sets all pixels to the chosen colour. The brightness parameter is a relative percentage of
    # the brightness that the NeoPixels were initialised with. The change will not be visible in
    # the NeoPixels until update() is called.
    def set_all(self, colour, brightness=1.0):
        for i in range(len(self.red)):
            self.set(i, colour, brightness)  # show all colors

    # Turns on a pixel; colour is maintained. The change will not be visible in the NeoPixels
    # until update() is called.
    def on(self, i):
        if i < 0 or i >= self.count:
            raise Exception("NeoPixels: Index %s is out of bounds!" % i)

        self.bright[i] = 1.0

    # Turns off a pixel; colour is maintained. The change will not be visible in the NeoPixels
    # until update() is called.
    def off(self, i):
        if i < 0 or i >= self.count:
            raise Exception("NeoPixels: Index %s is out of bounds!" % i)

        self.bright[i] = 0.0

    # Turns on all the lights; colour is maintained. The change will not be visible in the NeoPixels
    #     # until update() is called.
    def all_on(self):
        for i in range(len(self.red)):
            self.on(i)

    # Turns off all the lights; colour is maintained. The change will not be visible in the NeoPixels
    #     # until update() is called.
    def all_off(self):
        for i in range(len(self.red)):
            self.off(i)

    # Updates the physical NeoPixels to match any changes.
    def update(self):
        state = array.array("I", [0 for _ in range(self.count)])
        for i, colour in enumerate(self.red):
            r = int(self.red[i] * self.bright[i] * self.brightness) & 0xFF  # 8-bit red dimmed to brightness
            g = int(self.green[i] * self.bright[i] * self.brightness) & 0xFF  # 8-bit green dimmed to brightness
            b = int(self.blue[i] * self.bright[i] * self.brightness) & 0xFF  # 8-bit blue dimmed to brightness

            state[i] = (g << 16) + (r << 8) + b  # 24-bit color dimmed to brightness

        self.sm.put(state, 8)  # update the state machine with new colors


# Pulse fades all the NeoPixels from completely off to full brightness then back to completely off.
async def pulse_all(pixels, step=5):
    brightnesses = [ii for ii in range(0, 255, step)]
    brightnesses.extend([ii for ii in range(255, -1, -step)])
    for brightness in brightnesses:
        pixels.brightness = (brightness / 255)
        pixels.update()
        await asyncio.sleep_ms(20)


# This dims and brightens each neopixel that is "on" (has a brightness > 0). This function
# by default pulses each pixel but is configurable using every. The pulse is controlled with
# start and step which controls the lowest brightness and the speed with which it pulses.
async def pulse(pixels, start=100, step=25, every=1):
    brightnesses = [ii for ii in range(start, 255, step)]
    brightnesses.extend([ii for ii in range(255, start, -step)])
    for brightness in brightnesses:
        for i in range(0, pixels.count, every):
            if pixels.bright[i] > 0:
                pixels.bright[i] = (brightness / 255)
        pixels.update()
        await asyncio.sleep_ms(50)


# This flickers each neopixel that is "on" (has a brightness > 0). This function
# by default flickers each pixel but is configurable using every. The flicker
# sets the brightness of the pixels to a random value between base and (base + flame).
async def flicker(pixels, base=150, flame=105, every=1):
    for i in range(0, pixels.count, every):
        if pixels.bright[i] > 0:
            pixels.bright[i] = (base + random.randint(0, flame)) / 255
    pixels.update()
    await asyncio.sleep_ms(50)


# This is a useful test function that cycles the pixels through the
# supplied colours and fades then in and out.
async def cycle_colours_and_pulse(pixels, colors=[BLUE, YELLOW, CYAN, RED, GREEN, WHITE]):
    for colour in colors:
        pixels.set_all(colour)
        await pulse_all(pixels)


def init():
    pass

# There is no run() function as this is just designed to be used by other modules.
