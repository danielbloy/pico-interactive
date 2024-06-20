import asyncio

from environment import are_pins_available

# TODO: extract this out
SLEEP_INTERVAL = 0.1

if are_pins_available():

    import digitalio
    from adafruit_debouncer import Debouncer


    async def __button_loop():
        pin = digitalio.DigitalInOut(BUTTON_PIN)
        pin.direction = digitalio.Direction.INPUT
        pin.pull = digitalio.Pull.UP
        switch = Debouncer(pin)
        while True:
            await asyncio.sleep(SLEEP_INTERVAL / 1000)
            switch.update()
            if switch.rose:
                btn_event()


else:
    async def __button_loop():
        pass
        # Do something with a key


# Need some way to pass in pin or key
async def button_loop():
    while True:
        await asyncio.sleep(SLEEP_INTERVAL / 1000)
        # TODO: call the polyfill function
