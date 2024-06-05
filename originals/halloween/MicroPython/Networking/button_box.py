# The button box nodes have a button event that they can send and sounds.
# The button has a light that can be turned on or off.
import config
import messages
import pico
import sounds
import leds
import coordinator

from picozero import Button

import uasyncio as asyncio

BUTTON_LIGHT_OFF = '/button/light/off'
BUTTON_LIGHT_ON = '/button/light/on'

light_on = False
led = leds.LED(16, 0)


def button_pressed():
    if config.logging: print("Button pressed")
    turn_button_light_on()
    if config.coordinator is not None:
        # See https://www.joeltok.com/posts/2021-02-python-async-sync/
        loop = asyncio.get_event_loop()
        coroutine = coordinator.send_event_message(config.coordinator, config.button_event)
        loop.run_until_complete(coroutine)
    else:
        if config.logging: print("Coordinator not set, no event message sent.")


def button_released():
    if config.logging: print("Button released")


button = Button(17)
button.when_pressed = button_pressed
button.when_released = button_released


def turn_button_light_off():
    global light_on, led
    light_on = False
    led.off()


def turn_button_light_on():
    global light_on, led
    light_on = True
    led.on()


async def send_button_light_off_message(ip):
    if config.logging: print("Sending button light off message to %s." % ip)
    await pico.send_message(ip, "GET", BUTTON_LIGHT_OFF)


async def send_button_light_on_message(ip):
    if config.logging: print("Sending button light on message to %s." % ip)
    await pico.send_message(ip, "GET", BUTTON_LIGHT_ON)


async def respond_to_button_light_off(method, request, headers, response_headers):
    if config.logging: print("Responding to button light off message.")

    turn_button_light_off()

    response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = 'BUTTON LIGHT HAS BEEN TURNED OFF'
    return response_headers[pico.HEADER_DATA]


async def respond_to_button_light_on(method, request, headers, response_headers):
    if config.logging: print("Responding to button light on message.")
    turn_button_light_on()

    response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = 'BUTTON LIGHT HAS BEEN TURNED ON'
    return response_headers[pico.HEADER_DATA]


# This must not be too greedy otherwise it will interfere with the HTTP server.
async def background_tasks():
    global light_on, led
    while True:
        if light_on:
            led.on()
            await leds.pulse(led)
        else:
            led.off()

        await asyncio.sleep_ms(50)


def init():
    pico.message_responders[BUTTON_LIGHT_OFF] = respond_to_button_light_off
    pico.message_responders[BUTTON_LIGHT_ON] = respond_to_button_light_on
    sounds.init()


def run():
    init()
    messages.run(background_tasks)
