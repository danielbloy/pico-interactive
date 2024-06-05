# Co-ordinator code.
import time

import config
import directory
import messages
import pico
import sounds
import button_box
import cauldron_box
import path_box
import sensor_box

import uasyncio as asyncio

PATH_ROLE = "path"
CAULDRON_ROLE = "cauldron"
BUTTON_ROLE = "button"
SENSOR_ROLE = "sensor"

ENTER_BUTTON_NAME = "button-red"
DOOR_BUTTON_NAME = "button-blue"
PATH_LEFT_NAME = "path-left"
PATH_RIGHT_NAME = "path-right"
CAULDRON_NAME = "cauldron"


# All nodes (except the sensor box) have sounds. we do not do the sounds off concurrently
# as we will run out of memory.
async def all_sounds_off():
    if config.logging: print("Turning off all sounds.")
    endpoints = await directory.lookup_all_endpoints()
    for name, ip in endpoints.items():
        if name == "sensor-door":
            if config.logging: print("Ignoring the sensor box")

        if config.logging: print("Turning sounds off for node %s:%s" % (name, ip))
        await sounds.send_sounds_off_message(ip)


# All lights off on the path, cauldron and buttons.
async def all_lights_off():
    if config.logging: print("Turning off all lights.")

    tasks = []
    path_nodes = await directory.lookup_endpoints_by_role(PATH_ROLE)
    for name, ip in path_nodes.items():
        if config.logging: print("Turning lights off for path node %s:%s" % (name, ip))
        tasks.append(path_box.send_lights_off_message(ip))
    await asyncio.gather(*tasks)

    tasks = []
    button_nodes = await directory.lookup_endpoints_by_role(BUTTON_ROLE)
    for name, ip in button_nodes.items():
        if config.logging: print("Turning lights off for button node %s:%s" % (name, ip))
        tasks.append(button_box.send_button_light_off_message(ip))
    await asyncio.gather(*tasks)

    tasks = []
    cauldron_nodes = await directory.lookup_endpoints_by_role(CAULDRON_ROLE)
    for name, ip in cauldron_nodes.items():
        if config.logging: print("Turning lights off for cauldron node %s:%s" % (name, ip))
        tasks.append(cauldron_box.send_lights_off_message(ip))
    await asyncio.gather(*tasks)


async def reset_sensors():
    if config.logging: print("Resetting all sensors.")

    tasks = []
    sensor_nodes = await directory.lookup_endpoints_by_role(SENSOR_ROLE)
    for name, ip in sensor_nodes.items():
        if config.logging: print("Resetting sensor node %s:%s" % (name, ip))
        tasks.append(sensor_box.send_proximity_events_reset(ip))
    await asyncio.gather(*tasks)


# Dont allow the steps to have multiple concurrent executions
reset_all = False
reset_running = False
enter_running = False
ultrasonic_running = False
door_running = False


# This puts the setup into it's waiting state.
async def reset(headers):
    global reset_all, reset_running
    if reset_running:
        if config.logging: print("System reset already running, skipping.")
        return

    try:
        reset_running = True
        reset_all = True
        if config.logging: print("Running system reset.")

        # All sounds off except for the background noise.
        await all_sounds_off()

        # All lights off on the path, cauldron and buttons.
        await all_lights_off()

        # Reset the sensor box
        await reset_sensors()

        # Give everything else a chance to exit.
        await asyncio.sleep_ms(10000)

        # All sounds off except for the background noise.
        await all_sounds_off()

        # All lights off on the path, cauldron and buttons.
        await all_lights_off()

        # Reset the sensor box
        await reset_sensors()

        # Turn on the enter and door buttons
        enter_button = await directory.lookup_endpoint_by_name(ENTER_BUTTON_NAME)
        if len(enter_button) > 0:
            await button_box.send_button_light_on_message(enter_button)

        door_button = await directory.lookup_endpoint_by_name(DOOR_BUTTON_NAME)
        if len(door_button) > 0:
            await button_box.send_button_light_on_message(door_button)

    finally:
        reset_all = False
        reset_running = False


async def enter_button_pressed(headers):
    global reset_all, enter_running

    if enter_running:
        if config.logging: print("Enter button already running, skipping.")
        return

    try:
        enter_running = True
        if config.logging: print("Triggering enter button script.")

        enter_button = await directory.lookup_endpoint_by_name(ENTER_BUTTON_NAME)
        path_left = await directory.lookup_endpoint_by_name(PATH_LEFT_NAME)
        path_right = await directory.lookup_endpoint_by_name(PATH_RIGHT_NAME)
        cauldron = await directory.lookup_endpoint_by_name(CAULDRON_NAME)

        if reset_all:
            if config.logging: print("Reset triggered, aborting.")
            return

        # Trigger the church bells on path-left
        start = time.ticks_ms()
        deadline = time.ticks_add(start, 600)
        if len(path_left) > 0:
            await sounds.send_sounds_play_message(path_left, 1)

        # 1st dong
        while time.ticks_diff(deadline, time.ticks_ms()) > 0:
            await asyncio.sleep_ms(50)

        if reset_all:
            if config.logging: print("Reset triggered, aborting.")
            return

        tasks = []
        if len(path_left) > 0:
            tasks.append(path_box.send_lights_on_message(path_left, 2))
        if len(path_right) > 0:
            tasks.append(path_box.send_lights_on_message(path_right, 2))
        await asyncio.gather(*tasks)

        await asyncio.sleep_ms(1000)

        # Queue up bubbling and a witches laugh in the middle
        if len(cauldron) > 0:
            await sounds.send_sounds_play_message(cauldron, 4)
            await sounds.send_sounds_play_message(cauldron, 1)
            await sounds.send_sounds_play_message(cauldron, 1)

        await asyncio.sleep_ms(2000)

        # Turn on the cauldron
        if len(cauldron) > 0:
            await cauldron_box.send_lights_on_message(cauldron)

        # 2nd dong
        deadline = time.ticks_add(deadline, 5500)
        while time.ticks_diff(deadline, time.ticks_ms()) > 0:
            await asyncio.sleep_ms(50)

        if reset_all:
            if config.logging: print("Reset triggered, aborting.")
            return

        tasks = []
        if len(path_left) > 0:
            tasks.append(path_box.send_lights_on_message(path_left, 4))
        if len(path_right) > 0:
            tasks.append(path_box.send_lights_on_message(path_right, 4))
        await asyncio.gather(*tasks)

        # Queue up lion on path left for after the bells.
        if len(path_left) > 0:
            await sounds.send_sounds_play_message(path_left, 2)

        await asyncio.sleep_ms(1000)

        # Witches laugh
        if len(enter_button) > 0:
            await sounds.send_sounds_play_message(enter_button, 4)

        # 3rd dong
        deadline = time.ticks_add(deadline, 5500)
        while time.ticks_diff(deadline, time.ticks_ms()) > 0:
            await asyncio.sleep_ms(50)

        if reset_all:
            if config.logging: print("Reset triggered, aborting.")
            return

        tasks = []
        if len(path_left) > 0:
            tasks.append(path_box.send_lights_on_message(path_left, 6))
        if len(path_right) > 0:
            tasks.append(path_box.send_lights_on_message(path_right, 6))
        await asyncio.gather(*tasks)

        await asyncio.sleep_ms(3500)
        if reset_all:
            if config.logging: print("Reset triggered, aborting.")
            return
        # Now we are at about 15 seconds

        await asyncio.sleep_ms(5000)

        if reset_all:
            if config.logging: print("Reset triggered, aborting.")
            return

        # Dragon (lion will be playing at path left)
        if len(enter_button) > 0:
            await sounds.send_sounds_play_message(enter_button, 3)

        await asyncio.sleep_ms(5000)

        if reset_all:
            if config.logging: print("Reset triggered, aborting.")
            return
        # Now we are at about 25 seconds

        await asyncio.sleep_ms(5000)

        if reset_all:
            if config.logging: print("Reset triggered, aborting.")
            return

        # Lion
        if len(enter_button) > 0:
            await sounds.send_sounds_play_message(enter_button, 2)

        await asyncio.sleep_ms(5000)

        if reset_all:
            if config.logging: print("Reset triggered, aborting.")
            return

        await asyncio.sleep_ms(5000)

        if reset_all:
            if config.logging: print("Reset triggered, aborting.")
            return

        await asyncio.sleep_ms(2000)

        if reset_all:
            if config.logging: print("Reset triggered, aborting.")
            return
        # Now we are at about 45 seconds

        # Dragon
        if len(path_left) > 0:
            await sounds.send_sounds_play_message(path_left, 3)

        await asyncio.sleep_ms(5000)

        if reset_all:
            if config.logging: print("Reset triggered, aborting.")
            return

        # Lion
        if len(enter_button) > 0:
            await sounds.send_sounds_play_message(enter_button, 2)

        # We want this to all finish 60 seconds after the start
        deadline = time.ticks_add(start, 60000)
        while time.ticks_diff(deadline, time.ticks_ms()) > 0:
            await asyncio.sleep_ms(50)

        # Turn off skulls and cauldron
        tasks = []
        cauldron_nodes = await directory.lookup_endpoints_by_role(CAULDRON_ROLE)
        for name, ip in cauldron_nodes.items():
            if config.logging: print("Turning lights off for cauldron node %s:%s" % (name, ip))
            tasks.append(cauldron_box.send_lights_off_message(ip))
        await asyncio.gather(*tasks)

        tasks = []
        path_nodes = await directory.lookup_endpoints_by_role(PATH_ROLE)
        for name, ip in path_nodes.items():
            if config.logging: print("Turning lights off for path node %s:%s" % (name, ip))
            tasks.append(path_box.send_lights_off_message(ip))
        await asyncio.gather(*tasks)

    finally:
        enter_running = False


async def two_point_five_meter_trigger(headers):
    global reset_all, ultrasonic_running

    if ultrasonic_running:
        if config.logging: print("Ultrasonic event already running, skipping.")
        return

    try:
        ultrasonic_running = True
        if config.logging: print("Triggering ultrasonic script.")

        path_right = await directory.lookup_endpoint_by_name(PATH_RIGHT_NAME)

        # Dragon
        if len(path_right) > 0:
            await sounds.send_sounds_play_message(path_right, 2)

        await asyncio.sleep_ms(5000)

        if reset_all:
            if config.logging: print("Reset triggered, aborting.")
            return

        await asyncio.sleep_ms(5000)

        if reset_all:
            if config.logging: print("Reset triggered, aborting.")
            return

        await asyncio.sleep_ms(5000)

        if reset_all:
            if config.logging: print("Reset triggered, aborting.")
            return

        # Lion
        if len(path_right) > 0:
            await sounds.send_sounds_play_message(path_right, 1)

        await asyncio.sleep_ms(5000)

        if reset_all:
            if config.logging: print("Reset triggered, aborting.")
            return

        await asyncio.sleep_ms(5000)

        if reset_all:
            if config.logging: print("Reset triggered, aborting.")
            return

        await asyncio.sleep_ms(5000)

        if reset_all:
            if config.logging: print("Reset triggered, aborting.")
            return

    finally:
        ultrasonic_running = False
        # Reset itself
        await reset_sensors()


async def door_button_pressed(headers):
    global reset_all, door_running

    if door_running:
        if config.logging: print("Door already running, skipping.")
        return

    try:
        door_running = True
        if config.logging: print("Triggering door button script.")

        door_button = await directory.lookup_endpoint_by_name(DOOR_BUTTON_NAME)

        # Trigger the door to play end or begin, then prickling thumbs and then end or begin
        if len(door_button) > 0:
            await sounds.send_sounds_play_message(door_button, 1)
            await sounds.send_sounds_play_message(door_button, 2)
            await sounds.send_sounds_play_message(door_button, 1)

        await asyncio.sleep_ms(5000)

        if reset_all:
            if config.logging: print("Reset triggered, aborting.")
            return

        await asyncio.sleep_ms(5000)

        if reset_all:
            if config.logging: print("Reset triggered, aborting.")
            return

        await asyncio.sleep_ms(5000)

    finally:
        door_running = False


async def noop(headers):
    await messages.led_blink()


async def event_enter(headers):
    if config.logging: print("Enter event triggered '%s'" % "ENTER")
    asyncio.create_task(enter_button_pressed(headers))


async def event_two_point_five_meter(headers):
    if config.logging: print("2.5 meter event triggered '%s'" % "ENTER")
    asyncio.create_task(two_point_five_meter_trigger(headers))


async def event_door(headers):
    if config.logging: print("Door event triggered '%s'" % "DOOR")
    asyncio.create_task(door_button_pressed(headers))


EVENT_ENTER_BTN_PRESSED = "ENTER_BTN_PRESSED"
EVENT_DOOR_BTN_PRESSED = "DOOR_BTN_PRESSED"
EVENT_PROXIMITY_50 = "PROXIMITY_50"
EVENT_PROXIMITY_100 = "PROXIMITY_100"
EVENT_PROXIMITY_150 = "PROXIMITY_150"
EVENT_PROXIMITY_200 = "PROXIMITY_200"
EVENT_PROXIMITY_250 = "PROXIMITY_250"

event_handlers = {
    EVENT_ENTER_BTN_PRESSED: event_enter,
    EVENT_DOOR_BTN_PRESSED: event_door,
    EVENT_PROXIMITY_50: noop,
    EVENT_PROXIMITY_100: noop,
    EVENT_PROXIMITY_150: noop,
    EVENT_PROXIMITY_200: noop,
    EVENT_PROXIMITY_250: event_two_point_five_meter,
}

RESET = '/reset'  # Starts the sequence over
ENTER = '/enter/pressed'  # Useful trigger for remote control of enter button pressed
DIST_2_5 = '/distance/2.5'  # Useful trigger for remote control of 2.5 meter event
DOOR = '/door/pressed'  # Useful trigger for remote control of door button pressed

EVENT = '/event'  # The data indicates what event occurred


async def respond_to_reset(method, request, headers, response_headers):
    if config.logging: print("Responding to reset message.")

    asyncio.create_task(reset(headers))

    response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = 'RESET HAS BEEN PERFORMED'
    return response_headers[pico.HEADER_DATA]


async def respond_to_enter(method, request, headers, response_headers):
    if config.logging: print("Responding to enter button message.")

    asyncio.create_task(enter_button_pressed(headers))

    response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = 'ENTER BUTTON HAS BEEN PERFORMED'
    return response_headers[pico.HEADER_DATA]


async def respond_to_two_point_five_meter(method, request, headers, response_headers):
    if config.logging: print("Responding to 2.5 meter message.")

    asyncio.create_task(two_point_five_meter_trigger(headers))

    response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = '2.5 METER EVENT HAS BEEN PERFORMED'
    return response_headers[pico.HEADER_DATA]


async def respond_to_door(method, request, headers, response_headers):
    if config.logging: print("Responding to door button message.")

    asyncio.create_task(door_button_pressed(headers))

    response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = 'DOOR BUTTON HAS BEEN PERFORMED'
    return response_headers[pico.HEADER_DATA]


async def send_event_message(ip, event):
    if config.logging: print("Sending event %s message to %s." % (event, ip))
    await pico.send_message(ip, "GET", EVENT, event)


async def respond_to_event(method, request, headers, response_headers):
    if config.logging: print("Responding to event message.")

    # Extract event data header and check we know the event.
    event = headers[pico.HEADER_DATA]
    if event not in event_handlers:
        response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
        response_headers[pico.HEADER_DATA] = ('EVENT "%s" IS UNKNOWN' % event)
        return response_headers[pico.HEADER_DATA]

    handler = event_handlers[event]
    await handler(headers)

    response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = 'EVENT %s HAS BEEN TRIGGERED' % event
    return response_headers[pico.HEADER_DATA]


# This must not be too greedy otherwise it will interfere with the HTTP server.
async def background_tasks():
    while True:
        await asyncio.sleep_ms(50)


def init():
    pico.message_responders[RESET] = respond_to_reset
    pico.message_responders[EVENT] = respond_to_event
    pico.message_responders[ENTER] = respond_to_enter
    pico.message_responders[DIST_2_5] = respond_to_two_point_five_meter
    pico.message_responders[DOOR] = respond_to_door


def run():
    init()
    messages.run(background_tasks)
