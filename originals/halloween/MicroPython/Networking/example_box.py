# This is a sample application that repeatedly sends blink messages to all hardcoded
# known nodes. This is for testing only
import config
import directory
import messages
import pico

from picozero import Button

import uasyncio as asyncio

# Custom messages that can be triggered; these use the hard-coded list of nodes.
TURN_ON_ALL_LIGHTS = "/sample/all/on"
TURN_OFF_ALL_LIGHTS = "/sample/all/off"
BLINK_ALL_LIGHTS = "/sample/all/blink"

# Custom messages that can be triggered; these use the local-directory list of nodes.
DIRECTORY_BLINK_LOCAL_ALL_LIGHTS = "/sample/local-dir/blink/all"
DIRECTORY_BLINK_LOCAL_BLUE_ROLE_LIGHTS = "/sample/local-dir/blink/role/blue-role"
DIRECTORY_BLINK_LOCAL_PINK_NODE_LIGHTS = "/sample/local-dir/blink/node/pink"

# Custom messages that can be triggered; these use the remote-directory list of nodes.
DIRECTORY_BLINK_REMOTE_ALL_LIGHTS = "/sample/remote-dir/blink/all"
DIRECTORY_BLINK_REMOTE_GREEN_ROLE_LIGHTS = "/sample/remote-dir/blink/role/green-role"
DIRECTORY_BLINK_REMOTE_ORANGE_NODE_LIGHTS = "/sample/remote-dir/blink/node/orange"

# Constants for a hardcode list of nodes; i.e. not a directory lookup.
PINK = "192.168.1.165"
BLUE = "192.168.1.84"
GREEN = "192.168.1.164"
ORANGE = "192.168.1.72"
YELLOW = "192.168.1.225"

# nodes = [PINK, BLUE, GREEN, ORANGE, YELLOW]
nodes = [PINK, BLUE, GREEN, ORANGE]


# nodes = [YELLOW]


# Custom messages

async def respond_to_turn_on_all_lights(method, request, headers, response_headers):
    if config.logging: print("Responding to turn on all lights message.")

    tasks = [messages.send_light_on_message(node) for node in nodes]
    await asyncio.gather(*tasks)

    response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = 'LIGHTS ARE ON'
    return response_headers[pico.HEADER_DATA]


async def respond_to_turn_off_all_lights(method, request, headers, response_headers):
    if config.logging: print("Responding to turn off all lights message.")

    tasks = [messages.send_light_off_message(node) for node in nodes]
    await asyncio.gather(*tasks)

    response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = 'LIGHTS ARE OFF'
    return response_headers[pico.HEADER_DATA]


async def respond_to_blink_all_lights(method, request, headers, response_headers):
    if config.logging: print("Responding to blink all lights message.")

    tasks = [messages.send_light_blink_message(node) for node in nodes]
    await asyncio.gather(*tasks)

    response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = 'LIGHTS HAVE BLINKED'
    return response_headers[pico.HEADER_DATA]


pico.message_responders[TURN_ON_ALL_LIGHTS] = respond_to_turn_on_all_lights
pico.message_responders[TURN_OFF_ALL_LIGHTS] = respond_to_turn_off_all_lights
pico.message_responders[BLINK_ALL_LIGHTS] = respond_to_blink_all_lights


async def respond_to_directory_local_blink_all(method, request, headers, response_headers):
    if config.logging: print("Responding to local blink all nodes message.")

    all_nodes = await directory.lookup_all_endpoints()
    tasks = [messages.send_light_blink_message(ip) for ip in all_nodes.values()]
    await asyncio.gather(*tasks)

    response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = '%s LIGHTS HAVE BLINKED' % len(tasks)
    return response_headers[pico.HEADER_DATA]


async def respond_to_directory_local_blink_role_blue(method, request, headers, response_headers):
    if config.logging: print("Responding to local blink blue role message.")

    blue_role_nodes = await directory.lookup_endpoints_by_role("role-blue")
    tasks = [messages.send_light_blink_message(ip) for ip in blue_role_nodes.values()]
    await asyncio.gather(*tasks)

    response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = '%s BLUE LIGHTS HAVE BLINKED' % len(tasks)
    return response_headers[pico.HEADER_DATA]


async def respond_to_directory_local_blink_node_pink(method, request, headers, response_headers):
    if config.logging: print("Responding to local blink pink node message.")

    pink_node = await directory.lookup_endpoint_by_name("pink")
    if len(pink_node) > 0:
        await messages.send_light_blink_message(pink_node)

    response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = '%s PINK LIGHTS HAVE BLINKED' % (1 if len(pink_node) > 0 else 0)
    return response_headers[pico.HEADER_DATA]


pico.message_responders[DIRECTORY_BLINK_LOCAL_ALL_LIGHTS] = respond_to_directory_local_blink_all
pico.message_responders[DIRECTORY_BLINK_LOCAL_BLUE_ROLE_LIGHTS] = respond_to_directory_local_blink_role_blue
pico.message_responders[DIRECTORY_BLINK_LOCAL_PINK_NODE_LIGHTS] = respond_to_directory_local_blink_node_pink


async def respond_to_directory_remote_blink_all(method, request, headers, response_headers):
    if config.logging: print("Responding to remote blink all nodes message.")
    if config.coordinator is None:
        return

    all_ips = await messages.send_lookup_all_message(config.coordinator)
    tasks = [messages.send_light_blink_message(ip) for ip in all_ips]
    await asyncio.gather(*tasks)

    response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = '%s LIGHTS HAVE BLINKED' % len(tasks)
    return response_headers[pico.HEADER_DATA]


async def respond_to_directory_remote_blink_role_green(method, request, headers, response_headers):
    if config.logging: print("Responding to remote blink green role message.")
    if config.coordinator is None:
        return

    all_ips = await messages.send_lookup_role_message(config.coordinator, 'role-green')
    tasks = [messages.send_light_blink_message(ip) for ip in all_ips]
    await asyncio.gather(*tasks)

    response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = '%s GREEN LIGHTS HAVE BLINKED' % len(tasks)
    return response_headers[pico.HEADER_DATA]


async def respond_to_directory_remote_blink_node_orange(method, request, headers, response_headers):
    if config.logging: print("Responding to remote blink orange node message.")
    if config.coordinator is None:
        return

    ip = await messages.send_lookup_name_message(config.coordinator, 'orange')
    if len(ip) > 0:
        await messages.send_light_blink_message(ip)

    response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = '%s ORANGE LIGHTS HAVE BLINKED' % (1 if len(ip) > 0 else 0)
    return response_headers[pico.HEADER_DATA]


pico.message_responders[DIRECTORY_BLINK_REMOTE_ALL_LIGHTS] = respond_to_directory_remote_blink_all
pico.message_responders[DIRECTORY_BLINK_REMOTE_GREEN_ROLE_LIGHTS] = respond_to_directory_remote_blink_role_green
pico.message_responders[DIRECTORY_BLINK_REMOTE_ORANGE_NODE_LIGHTS] = respond_to_directory_remote_blink_node_orange

blinking_enabled = False
make_blink = False


async def blink_all_lights():
    if config.logging: print("Sending message to blink all lights.")
    tasks = [messages.send_light_blink_message(node) for node in nodes]
    await asyncio.gather(*tasks)


# This must not be too greedy otherwise it will interfere with the HTTP server.
async def background_tasks():
    global blinking_enabled, make_blink
    while True:
        if config.coordinator is not None:
            await messages.send_light_blink_message(config.coordinator)
            await asyncio.sleep(3)

        if make_blink:
            make_blink = False
            await blink_all_lights()

        if blinking_enabled:
            await blink_all_lights()
            await asyncio.sleep(5)

        await asyncio.sleep_ms(5)


#  Button code
button1 = Button(16)
button2 = Button(20)


def button1_event():
    if config.logging: print("***** Button 1 pressed")
    global make_blink
    make_blink = True


def button2_event():
    if config.logging: print("***** Button 2 pressed")
    global blinking_enabled
    blinking_enabled = not blinking_enabled


button1.when_pressed = button1_event
button2.when_pressed = button2_event

messages.run(background_tasks)
#messages.run()
