# The path nodes controls the lights and sounds down the walkway.
# There are six lights, each of which contains two neopixels.
import config
import messages
import pico
import neopixels
import sounds

import uasyncio as asyncio

# Custom sound messages that can be triggered.
LIGHTS_OFF = '/lights/off'
LIGHTS_ON = '/lights/on'  # The DATA header indicates the number of lights to enable.
LIGHTS_ON_1 = '/lights/on/1'
LIGHTS_ON_2 = '/lights/on/2'
LIGHTS_ON_3 = '/lights/on/3'
LIGHTS_ON_4 = '/lights/on/4'
LIGHTS_ON_5 = '/lights/on/5'
LIGHTS_ON_6 = '/lights/on/6'

# NeoPixels.
NUM_PIXELS = 12
lights_on = False
np = neopixels.NeoPixels(0, NUM_PIXELS)
np.set_all(neopixels.ORANGE)


async def turn_lights_off():
    global lights_on, np
    np.all_off()
    np.update()
    lights_on = False


async def turn_lights_on(num):
    global lights_on, np
    np.all_off()
    for i in range(num * 2):
        np.on(i)
    np.update()
    lights_on = True


async def send_lights_off_message(ip):
    if config.logging: print("Sending lights off message to %s." % ip)
    await pico.send_message(ip, "GET", LIGHTS_OFF)


async def send_lights_on_message(ip, num):
    if config.logging: print("Sending %s lights on message to %s." % (num, ip))
    await pico.send_message(ip, "GET", LIGHTS_ON, str(num))


async def respond_to_lights_off(method, request, headers, response_headers):
    if config.logging: print("Responding to lights off message.")
    await turn_lights_off()

    response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = 'ALL LIGHTS HAVE BEEN TURNED OFF'
    return response_headers[pico.HEADER_DATA]


async def respond_to_lights_on(method, request, headers, response_headers):
    if config.logging: print("Responding to lights on message.")
    # Extract number of lights from data header and check range value
    num = int(headers[pico.HEADER_DATA])
    if num < 0 or num > 6:
        response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
        response_headers[pico.HEADER_DATA] = ('%s IS OUT OF RANGE' % num)
        return response_headers[pico.HEADER_DATA]

    await turn_lights_on(num)

    response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = '%s LIGHTS HAVE BEEN TURNED ON' % num
    return response_headers[pico.HEADER_DATA]


async def respond_to_lights_on_1(method, request, headers, response_headers):
    headers[pico.HEADER_DATA] = '1'
    return await respond_to_lights_on(method, request, headers, response_headers)


async def respond_to_lights_on_2(method, request, headers, response_headers):
    headers[pico.HEADER_DATA] = '2'
    return await respond_to_lights_on(method, request, headers, response_headers)


async def respond_to_lights_on_3(method, request, headers, response_headers):
    headers[pico.HEADER_DATA] = '3'
    return await respond_to_lights_on(method, request, headers, response_headers)


async def respond_to_lights_on_4(method, request, headers, response_headers):
    headers[pico.HEADER_DATA] = '4'
    return await respond_to_lights_on(method, request, headers, response_headers)


async def respond_to_lights_on_5(method, request, headers, response_headers):
    headers[pico.HEADER_DATA] = '5'
    return await respond_to_lights_on(method, request, headers, response_headers)


async def respond_to_lights_on_6(method, request, headers, response_headers):
    headers[pico.HEADER_DATA] = '6'
    return await respond_to_lights_on(method, request, headers, response_headers)


# This must not be too greedy otherwise it will interfere with the HTTP server.
async def background_tasks():
    global lights_on
    while True:
        if lights_on:
            await neopixels.flicker(np, every=2)

        await asyncio.sleep_ms(50)


def init():
    pico.message_responders[LIGHTS_OFF] = respond_to_lights_off
    pico.message_responders[LIGHTS_ON] = respond_to_lights_on
    pico.message_responders[LIGHTS_ON_1] = respond_to_lights_on_1
    pico.message_responders[LIGHTS_ON_2] = respond_to_lights_on_2
    pico.message_responders[LIGHTS_ON_3] = respond_to_lights_on_3
    pico.message_responders[LIGHTS_ON_4] = respond_to_lights_on_4
    pico.message_responders[LIGHTS_ON_5] = respond_to_lights_on_5
    pico.message_responders[LIGHTS_ON_6] = respond_to_lights_on_6
    sounds.init()
    neopixels.init()


def run():
    init()
    messages.run(background_tasks)
