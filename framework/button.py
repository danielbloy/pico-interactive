# TODO: Single press event
# TODO: Double press event
# TODO: Long press event


# This needs a polyfill that works on Desktop without Blinka.
# Rather than button, use key on desktop.

import asyncio

import digitalio
from adafruit_debouncer import Debouncer


def button_event():
    if music:
        if music.paused:
            music.resume()
        else:
            music.pause()


btn_event = button_event


async def button_loop():
    pin = digitalio.DigitalInOut(BUTTON_PIN)
    pin.direction = digitalio.Direction.INPUT
    pin.pull = digitalio.Pull.UP
    switch = Debouncer(pin)
    while btn_event:
        await asyncio.sleep(SLEEP_INTERVAL / 1000)
        switch.update()
        if switch.rose:
            btn_event()
