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

reset_all = False


# When the 2.5 metre event is triggered
# =====================================
# Trigger the bubbling cauldron on a cycle for 2 minutes.
# Flash the path lights and change the colours to green
# Trigger the lion from enter button
# Trigger the dragon from path right

# When the 1 metre event is triggered
# ===================================
# Trigger the door to play prickling thumbs
# Trigger the dragon from enter button
# Trigger the lion from path-right
# Trigger the laugh from path-left

# When the door (blue) button is pressed
# ======================================
# Trigger the witches laugh 2 from path-left
# Trigger heart beat from the door button
# Turn off the skulls or flash them.

# 30 seconds later repeat the church bells and lights down the path

# When the 2.5 metre point is triggered as they are walking away, lions roar from multiple places.

# 30 seconds later. Reset.

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


# This puts the setup into it's waiting state.
async def reset(headers):
    global reset_all
    if config.logging: print("Running system reset.")
    reset_all = True

    # All sounds off except for the background noise.
    await all_sounds_off()

    # All lights off on the path, cauldron and buttons.
    await all_lights_off()

    # Reset the sensor box
    await reset_sensors()

    # TODO: Turn the face off

    # Turn on the enter button
    enter_button = await directory.lookup_endpoint_by_name(ENTER_BUTTON_NAME)
    if len(enter_button) > 0:
        await button_box.send_button_light_on_message(enter_button)

    # Give everything else a chance to exit.
    await asyncio.sleep_ms(1000)
    reset_all = False


async def enter_button_pressed(headers):
    global reset_all
    if config.logging: print("Triggering enter button script.")

    # Enter (red) Button Pressed
    # ==========================
    # This is the trigger for the program to start.
    await reset_sensors()

    enter_button = await directory.lookup_endpoint_by_name(ENTER_BUTTON_NAME)
    door_button = await directory.lookup_endpoint_by_name(DOOR_BUTTON_NAME)
    path_left = await directory.lookup_endpoint_by_name(PATH_LEFT_NAME)
    path_right = await directory.lookup_endpoint_by_name(PATH_RIGHT_NAME)
    cauldron = await directory.lookup_endpoint_by_name(CAULDRON_NAME)

    if reset_all:
        if config.logging: print("Reset triggered, aborting.")
        return

    # Trigger the enter button with witches laugh 1.
    if len(enter_button) > 0:
        await sounds.send_sounds_play_message(enter_button, 4)

    # Trigger the church bells on path-left
    # In time with each dong, turn on the lights on path-left at the following points (after triggering):
    #  - 1 second
    #  - 6 seconds
    #  - 12 seconds
    #  - 17 seconds
    #  - 23 seconds
    #  - 28 seconds
    if reset_all:
        if config.logging: print("Reset triggered, aborting.")
        return

    deadline = time.ticks_add(time.ticks_ms(), 600)
    if len(path_left) > 0:
        await sounds.send_sounds_play_message(path_left, 1)

    # 1st dong - trigger the door with end or begin
    while time.ticks_diff(deadline, time.ticks_ms()) > 0:
        await asyncio.sleep_ms(50)
    deadline = time.ticks_add(deadline, 5500)

    if reset_all:
        if config.logging: print("Reset triggered, aborting.")
        return

    tasks = []
    if len(path_left) > 0:
        tasks.append(path_box.send_lights_on_message(path_left, 1))
    if len(path_right) > 0:
        tasks.append(path_box.send_lights_on_message(path_right, 1))
    await asyncio.gather(*tasks)

    if len(door_button) > 0:
        await sounds.send_sounds_play_message(door_button, 1)

    # 2nd dong
    while time.ticks_diff(deadline, time.ticks_ms()) > 0:
        await asyncio.sleep_ms(50)
    deadline = time.ticks_add(deadline, 5500)

    if reset_all:
        if config.logging: print("Reset triggered, aborting.")
        return

    tasks = []
    if len(path_left) > 0:
        tasks.append(path_box.send_lights_on_message(path_left, 2))
    if len(path_right) > 0:
        tasks.append(path_box.send_lights_on_message(path_right, 2))
    await asyncio.gather(*tasks)

    # 3rd dong - trigger the cauldron with prickling thumbs
    while time.ticks_diff(deadline, time.ticks_ms()) > 0:
        await asyncio.sleep_ms(50)
    deadline = time.ticks_add(deadline, 5500)

    if reset_all:
        if config.logging: print("Reset triggered, aborting.")
        return

    tasks = []
    if len(path_left) > 0:
        tasks.append(path_box.send_lights_on_message(path_left, 3))
    if len(path_right) > 0:
        tasks.append(path_box.send_lights_on_message(path_right, 3))
    await asyncio.gather(*tasks)

    if len(cauldron) > 0:
        await sounds.send_sounds_play_message(cauldron, 2)

    # 4th dong
    while time.ticks_diff(deadline, time.ticks_ms()) > 0:
        await asyncio.sleep_ms(50)
    deadline = time.ticks_add(deadline, 5500)

    if reset_all:
        if config.logging: print("Reset triggered, aborting.")
        return

    tasks = []
    if len(path_left) > 0:
        tasks.append(path_box.send_lights_on_message(path_left, 4))
    if len(path_right) > 0:
        tasks.append(path_box.send_lights_on_message(path_right, 4))
    await asyncio.gather(*tasks)

    # 5th dong - trigger the path-right with lion
    while time.ticks_diff(deadline, time.ticks_ms()) > 0:
        await asyncio.sleep_ms(50)
    deadline = time.ticks_add(deadline, 5500)

    if reset_all:
        if config.logging: print("Reset triggered, aborting.")
        return

    tasks = []
    if len(path_left) > 0:
        tasks.append(path_box.send_lights_on_message(path_left, 5))
    if len(path_right) > 0:
        tasks.append(path_box.send_lights_on_message(path_right, 5))
    await asyncio.gather(*tasks)

    if len(path_right) > 0:
        await sounds.send_sounds_play_message(path_right, 1)

    # 6th dong - TODO: trigger the face eyes on.
    while time.ticks_diff(deadline, time.ticks_ms()) > 0:
        await asyncio.sleep_ms(50)
    deadline = time.ticks_add(deadline, 5500)

    if reset_all:
        if config.logging: print("Reset triggered, aborting.")
        return

    tasks = []
    if len(path_left) > 0:
        tasks.append(path_box.send_lights_on_message(path_left, 6))
    if len(path_right) > 0:
        tasks.append(path_box.send_lights_on_message(path_right, 6))
    await asyncio.gather(*tasks)

    # Turn on the door button
    if len(door_button) > 0:
        await button_box.send_button_light_on_message(door_button)


async def two_point_five_meter_trigger(headers):
    enter_button = await directory.lookup_endpoint_by_name(ENTER_BUTTON_NAME)
    path_right = await directory.lookup_endpoint_by_name(PATH_RIGHT_NAME)
    cauldron = await directory.lookup_endpoint_by_name(CAULDRON_NAME)

    # Trigger the bubbling cauldron on a cycle for 2 minutes.
    if len(cauldron) > 0:
        await cauldron_box.send_lights_on_message(cauldron)
        await sounds.send_sounds_play_message(cauldron, 1)

    # Trigger the lion from enter button
    if len(enter_button) > 0:
        await sounds.send_sounds_play_message(enter_button, 2)

    # TODO: Flash the path lights and change the colours to green

    if len(cauldron) > 0:
        await sounds.send_sounds_play_message(cauldron, 1)
        await sounds.send_sounds_play_message(cauldron, 1)
        await sounds.send_sounds_play_message(cauldron, 1)
        await sounds.send_sounds_play_message(cauldron, 1)

    await asyncio.sleep_ms(2000)

    # Trigger the dragon from path right
    if len(path_right) > 0:
        await sounds.send_sounds_play_message(path_right, 2)


async def one_meter_trigger(headers):
    enter_button = await directory.lookup_endpoint_by_name(ENTER_BUTTON_NAME)
    door_button = await directory.lookup_endpoint_by_name(DOOR_BUTTON_NAME)
    path_left = await directory.lookup_endpoint_by_name(PATH_LEFT_NAME)
    path_right = await directory.lookup_endpoint_by_name(PATH_RIGHT_NAME)
    cauldron = await directory.lookup_endpoint_by_name(CAULDRON_NAME)

    # Trigger the door to play prickling thumbs
    if len(door_button) > 0:
        await sounds.send_sounds_play_message(door_button, 2)

    # Trigger the dragon from enter button
    if len(enter_button) > 0:
        await sounds.send_sounds_play_message(enter_button, 3)

    # Trigger the lion from path right
    if len(path_right) > 0:
        await sounds.send_sounds_play_message(path_right, 1)

    # Trigger the laugh from path-left
    if len(path_left) > 0:
        await sounds.send_sounds_play_message(path_left, 4)


async def door_button_pressed(headers):
    global reset_all
    if config.logging: print("Triggering door button script.")

    enter_button = await directory.lookup_endpoint_by_name(ENTER_BUTTON_NAME)
    door_button = await directory.lookup_endpoint_by_name(DOOR_BUTTON_NAME)
    path_left = await directory.lookup_endpoint_by_name(PATH_LEFT_NAME)
    path_right = await directory.lookup_endpoint_by_name(PATH_RIGHT_NAME)

    if reset_all:
        if config.logging: print("Reset triggered, aborting.")
        return

    # Trigger the witches laugh 2 from path-left
    deadline = time.ticks_add(time.ticks_ms(), 2000)
    if len(path_left) > 0:
        await sounds.send_sounds_play_message(path_left, 2)

    # TODO: Flash the skulls them.

    # Trigger heart beat from the door button
    while time.ticks_diff(deadline, time.ticks_ms()) > 0:
        await asyncio.sleep_ms(50)
    deadline = time.ticks_add(deadline, 30000)

    if len(door_button) > 0:
        await sounds.send_sounds_play_message(door_button, 3)
        await sounds.send_sounds_play_message(door_button, 3)
        await sounds.send_sounds_play_message(door_button, 3)

    # 30 seconds later repeat the church bells and lights down the path with multiple lion and dragons roars
    while time.ticks_diff(deadline, time.ticks_ms()) > 0:
        await asyncio.sleep_ms(50)

    # Trigger the church bells on path-left
    # In time with each dong, turn on the lights on path-left at the following points (after triggering):
    #  - 1 second
    #  - 6 seconds
    #  - 12 seconds
    #  - 17 seconds
    #  - 23 seconds
    #  - 28 seconds
    if reset_all:
        if config.logging: print("Reset triggered, aborting.")
        return

    deadline = time.ticks_add(time.ticks_ms(), 600)
    if len(path_left) > 0:
        await sounds.send_sounds_play_message(path_left, 1)

    # 1st dong -
    while time.ticks_diff(deadline, time.ticks_ms()) > 0:
        await asyncio.sleep_ms(50)
    deadline = time.ticks_add(deadline, 5500)

    if reset_all:
        if config.logging: print("Reset triggered, aborting.")
        return

    tasks = []
    if len(path_left) > 0:
        tasks.append(path_box.send_lights_on_message(path_left, 1))
    if len(path_right) > 0:
        tasks.append(path_box.send_lights_on_message(path_right, 1))
    await asyncio.gather(*tasks)

    # Witches laugh 1
    if len(enter_button) > 0:
        await sounds.send_sounds_play_message(enter_button, 4)

    # 2nd dong
    while time.ticks_diff(deadline, time.ticks_ms()) > 0:
        await asyncio.sleep_ms(50)
    deadline = time.ticks_add(deadline, 5500)

    if reset_all:
        if config.logging: print("Reset triggered, aborting.")
        return

    tasks = []
    if len(path_left) > 0:
        tasks.append(path_box.send_lights_on_message(path_left, 2))
    if len(path_right) > 0:
        tasks.append(path_box.send_lights_on_message(path_right, 2))
    await asyncio.gather(*tasks)

    # 3rd dong
    while time.ticks_diff(deadline, time.ticks_ms()) > 0:
        await asyncio.sleep_ms(50)
    deadline = time.ticks_add(deadline, 5500)

    if reset_all:
        if config.logging: print("Reset triggered, aborting.")
        return

    tasks = []
    if len(path_left) > 0:
        tasks.append(path_box.send_lights_on_message(path_left, 3))
    if len(path_right) > 0:
        tasks.append(path_box.send_lights_on_message(path_right, 3))
    await asyncio.gather(*tasks)

    # Dragon and lion
    if len(door_button) > 0:
        await sounds.send_sounds_play_message(door_button, 4)

    if len(path_right) > 0:
        await sounds.send_sounds_play_message(path_right, 2)

    # 4th dong
    while time.ticks_diff(deadline, time.ticks_ms()) > 0:
        await asyncio.sleep_ms(50)
    deadline = time.ticks_add(deadline, 5500)

    if reset_all:
        if config.logging: print("Reset triggered, aborting.")
        return

    tasks = []
    if len(path_left) > 0:
        tasks.append(path_box.send_lights_on_message(path_left, 4))
    if len(path_right) > 0:
        tasks.append(path_box.send_lights_on_message(path_right, 4))
    await asyncio.gather(*tasks)

    # Lion
    if len(enter_button) > 0:
        await sounds.send_sounds_play_message(enter_button, 2)

    # 5th dong
    while time.ticks_diff(deadline, time.ticks_ms()) > 0:
        await asyncio.sleep_ms(50)
    deadline = time.ticks_add(deadline, 5500)

    if reset_all:
        if config.logging: print("Reset triggered, aborting.")
        return

    tasks = []
    if len(path_left) > 0:
        tasks.append(path_box.send_lights_on_message(path_left, 5))
    if len(path_right) > 0:
        tasks.append(path_box.send_lights_on_message(path_right, 5))
    await asyncio.gather(*tasks)

    # Dragon
    if len(path_right) > 0:
        await sounds.send_sounds_play_message(path_right, 2)

    # 6th dong - TODO: turn off the face with eyes on.
    while time.ticks_diff(deadline, time.ticks_ms()) > 0:
        await asyncio.sleep_ms(50)
    deadline = time.ticks_add(deadline, 30000)

    if reset_all:
        if config.logging: print("Reset triggered, aborting.")
        return

    tasks = []
    if len(path_left) > 0:
        tasks.append(path_box.send_lights_on_message(path_left, 6))
    if len(path_right) > 0:
        tasks.append(path_box.send_lights_on_message(path_right, 6))
    await asyncio.gather(*tasks)

    # 60 seconds later. Reset.
    while time.ticks_diff(deadline, time.ticks_ms()) > 0:
        await asyncio.sleep_ms(50)

    await reset(headers)


async def noop(headers):
    await messages.led_blink()


async def event_enter(headers):
    if config.logging: print("Enter event triggered '%s'" % "ENTER")
    asyncio.create_task(enter_button_pressed(headers))


async def event_two_point_five_meter(headers):
    if config.logging: print("2.5 meter event triggered '%s'" % "ENTER")
    asyncio.create_task(two_point_five_meter_trigger(headers))


async def event_one_meter(headers):
    if config.logging: print("1 meter event triggered '%s'" % "ENTER")
    asyncio.create_task(one_meter_trigger(headers))


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
    EVENT_PROXIMITY_100: event_one_meter,
    EVENT_PROXIMITY_150: noop,
    EVENT_PROXIMITY_200: noop,
    EVENT_PROXIMITY_250: event_two_point_five_meter,
}

RESET = '/reset'  # Starts the sequence over
ENTER = '/enter/pressed'  # Useful trigger for remote control of enter button pressed
DIST_2_5 = '/distance/2.5'  # Useful trigger for remote control of 2.5 meter event
DIST_1 = '/distance/1'  # Useful trigger for remote control of 1 meter event
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


async def respond_to_one_meter(method, request, headers, response_headers):
    if config.logging: print("Responding to 1 meter message.")

    asyncio.create_task(one_meter_trigger(headers))

    response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = '1 METER EVENT HAS BEEN PERFORMED'
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
    pico.message_responders[DIST_1] = respond_to_one_meter
    pico.message_responders[DOOR] = respond_to_door


def run():
    init()
    messages.run(background_tasks)
