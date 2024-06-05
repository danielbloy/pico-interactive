# Almost all nodes support sounds so this is designed to be used in combination
# with other modules. Simply call init() to ensure all messages are registered.
# Remember, this module does not play sounds. It responds to sound messages and
# signals for the sound board to play sounds.

import config
import messages
import neopixels
import pico

import uasyncio as asyncio
from machine import Pin

# Custom sound messages that can be triggered.
SOUNDS_OFF = '/sounds/off'  # Signal for all sounds to stop.
SOUNDS_PLAY = '/sounds/play'  # The DATA header indicates the sound to play.
SOUNDS_PLAY_1 = '/sounds/play/1'
SOUNDS_PLAY_2 = '/sounds/play/2'
SOUNDS_PLAY_3 = '/sounds/play/3'
SOUNDS_PLAY_4 = '/sounds/play/4'
SOUNDS_PLAY_5 = '/sounds/play/5'
SOUNDS_PLAY_6 = '/sounds/play/6'

# Pins to trigger sounds. The first index is the pin to cancel all sounds.
pins = [
    Pin(15, Pin.OUT),  # Cancel sounds pin.
    Pin(14, Pin.OUT),
    Pin(13, Pin.OUT),
    Pin(12, Pin.OUT),
    Pin(11, Pin.OUT),
    Pin(10, Pin.OUT),
    Pin(9, Pin.OUT)
]
for pin in pins:
    pin.value(0)


async def turn_sounds_off():
    global pins
    pins[0].value(1)
    await asyncio.sleep_ms(50)
    pins[0].value(0)


async def play_sound(num):
    global pins
    pins[num].value(1)
    await asyncio.sleep_ms(50)
    pins[num].value(0)


async def send_sounds_off_message(ip):
    if config.logging: print("Sending sounds off message to %s." % ip)
    await pico.send_message(ip, "GET", SOUNDS_OFF)


async def send_sounds_play_message(ip, num):
    if config.logging: print("Sending play sound %s message to %s." % (num, ip))
    await pico.send_message(ip, "GET", SOUNDS_PLAY, str(num))


async def respond_to_sounds_off(method, request, headers, response_headers):
    await turn_sounds_off()

    response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = 'SOUNDS HAVE BEEN TURNED OFF'
    return response_headers[pico.HEADER_DATA]


async def respond_to_sounds_play(method, request, headers, response_headers):
    if config.logging: print("Responding to sounds play message.")
    # Extract number of sound from data header and check range value
    data_header = headers[pico.HEADER_DATA]
    if len(data_header) <= 0:
        if config.logging: print("No header data specified.")
        response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
        response_headers[pico.HEADER_DATA] = 'NO VALUE SPECIFIED FOR DATA HEADER'
        return response_headers[pico.HEADER_DATA]

    num = int(data_header)
    if num < 1 or num > 6:
        if config.logging: print("Data %s is out of range." % num)
        response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
        response_headers[pico.HEADER_DATA] = ('%s IS OUT OF RANGE' % num)
        return response_headers[pico.HEADER_DATA]

    await play_sound(num)

    response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = 'SOUND %s HAS BEEN TRIGGERED' % num
    return response_headers[pico.HEADER_DATA]


async def respond_to_sounds_play_1(method, request, headers, response_headers):
    headers[pico.HEADER_DATA] = '1'
    return await respond_to_sounds_play(method, request, headers, response_headers)


async def respond_to_sounds_play_2(method, request, headers, response_headers):
    headers[pico.HEADER_DATA] = '2'
    return await respond_to_sounds_play(method, request, headers, response_headers)


async def respond_to_sounds_play_3(method, request, headers, response_headers):
    headers[pico.HEADER_DATA] = '3'
    return await respond_to_sounds_play(method, request, headers, response_headers)


async def respond_to_sounds_play_4(method, request, headers, response_headers):
    headers[pico.HEADER_DATA] = '4'
    return await respond_to_sounds_play(method, request, headers, response_headers)


async def respond_to_sounds_play_5(method, request, headers, response_headers):
    headers[pico.HEADER_DATA] = '5'
    return await respond_to_sounds_play(method, request, headers, response_headers)


async def respond_to_sounds_play_6(method, request, headers, response_headers):
    headers[pico.HEADER_DATA] = '6'
    return await respond_to_sounds_play(method, request, headers, response_headers)


def init():
    pico.message_responders[SOUNDS_OFF] = respond_to_sounds_off
    pico.message_responders[SOUNDS_PLAY] = respond_to_sounds_play
    pico.message_responders[SOUNDS_PLAY_1] = respond_to_sounds_play_1
    pico.message_responders[SOUNDS_PLAY_2] = respond_to_sounds_play_2
    pico.message_responders[SOUNDS_PLAY_3] = respond_to_sounds_play_3
    pico.message_responders[SOUNDS_PLAY_4] = respond_to_sounds_play_4
    pico.message_responders[SOUNDS_PLAY_5] = respond_to_sounds_play_5
    pico.message_responders[SOUNDS_PLAY_6] = respond_to_sounds_play_6

# There is no run() function as this is just designed to be used by other modules.
