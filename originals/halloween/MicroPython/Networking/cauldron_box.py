# The path nodes controls the lights and sounds in the cauldron
# There are 12 neopixels.
import config
import messages
import pico
import neopixels
import sounds

import uasyncio as asyncio

LIGHTS_OFF = '/lights/off'
LIGHTS_ON = '/lights/on'

# NeoPixels.
NUM_PIXELS = 12
lights_on = False
np = neopixels.NeoPixels(0, NUM_PIXELS)
np.set_all(neopixels.GREEN)


async def turn_lights_off():
    global lights_on, np
    np.all_off()
    np.update()
    lights_on = False


async def turn_lights_on():
    global lights_on, np
    np.all_on()
    np.update()
    lights_on = True


async def send_lights_off_message(ip):
    if config.logging: print("Sending lights off message to %s." % ip)
    await pico.send_message(ip, "GET", LIGHTS_OFF)


async def send_lights_on_message(ip):
    if config.logging: print("Sending lights on message to %s." % ip)
    await pico.send_message(ip, "GET", LIGHTS_ON)


async def respond_to_lights_off(method, request, headers, response_headers):
    if config.logging: print("Responding to lights off message.")

    await turn_lights_off()

    response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = 'ALL LIGHTS HAVE BEEN TURNED OFF'
    return response_headers[pico.HEADER_DATA]


async def respond_to_lights_on(method, request, headers, response_headers):
    if config.logging: print("Responding to lights on message.")

    await turn_lights_on()

    response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = 'ALL LIGHTS HAVE BEEN TURNED ON'
    return response_headers[pico.HEADER_DATA]


# This must not be too greedy otherwise it will interfere with the HTTP server.
async def background_tasks():
    global lights_on
    while True:
        if lights_on:
            await neopixels.flicker(np, every=1)

        await asyncio.sleep_ms(50)


def init():
    pico.message_responders[LIGHTS_OFF] = respond_to_lights_off
    pico.message_responders[LIGHTS_ON] = respond_to_lights_on
    sounds.init()
    neopixels.init()


def run():
    init()
    messages.run(background_tasks)
