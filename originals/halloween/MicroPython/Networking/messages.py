import config
import pico
import directory

VERSION: str = "0.3.9"

import os, gc, machine
import uasyncio as asyncio

import time

# Well-known HTTP headers.
HEADER_CONTENT_TYPE = 'Content-type'
CONTENT_TYPE_PLAIN = 'text/plain'
CONTENT_TYPE_HTML = 'text/html'

# All nodes
ROOT_MESSAGE = '/'
INSPECT_MESSAGE = '/inspect'
LED_ON_MESSAGE = "/led/on"
LED_OFF_MESSAGE = "/led/off"
LED_BLINK_MESSAGE = "/led/blink"

# Primarily for endpoint nodes
ALIVE_MESSAGE = '/alive'
ROLE_MESSAGE = '/role'
NAME_MESSAGE = '/name'
RESTART_MESSAGE = '/restart'
REGISTER_SELF_MESSAGE = '/register/self'
UNREGISTER_SELF_MESSAGE = '/unregister/self'

# Primarily for coordinator nodes
REGISTER_MESSAGE = '/register'
UNREGISTER_MESSAGE = '/unregister'
HEARTBEAT_MESSAGE = '/heartbeat'
LOOKUP_ALL_MESSAGE = '/lookup/all'
LOOKUP_NAME_MESSAGE = '/lookup/name'
LOOKUP_ROLE_MESSAGE = '/lookup/role'

ALIVE_RESPONSE_YES = 'Yes'
RESTART_RESPONSE_YES = 'Yes'
REGISTER_RESPONSE_YES = 'Registered'
REGISTER_RESPONSE_NO = 'No coordinator'
UNREGISTER_RESPONSE_YES = 'Unregistered'
UNREGISTER_RESPONSE_NO = 'No coordinator'

from machine import Pin

onboard_led = Pin("LED", Pin.OUT, value=0)


async def restart_node(seconds):
    await asyncio.sleep(seconds)
    machine.reset()


# ********************************************************************************
# Standard response handlers for all nodes
# ********************************************************************************
# Status response which returns a web page of all node data.
async def respond_to_inspect_message(method, request, headers, response_headers):
    html = """<!DOCTYPE html>
    <html>
        <head><title>%s Inspect</title></head>
        <body>
            <h1>Inspect details for node: %s</h1>
            <p>Network: %s</p>
            <p>IP Address: %s</p>
            <p>Version of pico.py: %s</p>
            <p>Version of directory.py: %s</p>
            <p>Version of messages.py: %s</p>
            <p>Name: %s</p>
            <p>Coordinator: %s</p>
            <p>Role: %s</p>
            <p>Logging: %s</p>
            <h2>Machine info</h2>
            <p>CPU Frequency: %s Mhz</p>
            <p>Heap RAM used: %s bytes</p>
            <p>Heap RAM free: %s bytes</p>
            <p>Free storage: %s Kb</p>
            <h2>Supported messages</h2>
            %s
            %s
        </body>
    </html>
    """
    supported_messages = ""
    try:
        for route in sorted(pico.message_responders):
            supported_messages += "<p>%s</p>" % route
    except:
        if config.logging: print("An exception occurred producing supported messages for inspect!")

    nodes = "<h2>Directory</h2><p>Time now: %s</p>" % time.time()

    try:
        for key, value in directory.directory.items():
            nodes += ("<p>%s has IP: %s; Role: %s; Expiry: %s</p>" %
                      (key, value[directory.IP], value[directory.ROLE], value[directory.EXPIRE]))
    except:
        if config.logging: print("An exception occurred producing directory of nodes for inspect!")

    # From: https://raspberrypi.stackexchange.com/questions/140902/useful-statistics-from-pi-pico
    cpu_freq = machine.freq() / 1000000
    heap_ram_used = gc.mem_alloc()
    heap_ram_free = gc.mem_free()
    s = os.statvfs('/')
    storage_free = s[0] * s[3] / 1024

    response = html % (
        config.name,
        config.name,
        config.ssid,
        pico.ip,
        pico.VERSION,
        directory.VERSION,
        VERSION,
        config.name,
        config.coordinator,
        config.role,
        config.logging,
        cpu_freq,
        heap_ram_used,
        heap_ram_free,
        storage_free,
        supported_messages,
        nodes,
    )

    response_headers[HEADER_CONTENT_TYPE] = CONTENT_TYPE_HTML
    return response


async def respond_to_led_on(method, request, headers, response_headers):
    onboard_led.on()
    response_headers[pico.HEADER_DATA] = 'ON'
    return 'LED is ON'


async def respond_to_led_off(method, request, headers, response_headers):
    onboard_led.off()
    response_headers[pico.HEADER_DATA] = 'OFF'
    return 'LED is OFF'


async def led_blink():
    onboard_led.on()
    await asyncio.sleep(0.25)
    onboard_led.off()


async def respond_to_led_blink(method, request, headers, response_headers):
    asyncio.create_task(led_blink())
    response_headers[pico.HEADER_DATA] = 'BLINK'
    return 'LED has BLINKED'


pico.message_responders[ROOT_MESSAGE] = respond_to_inspect_message
pico.message_responders[INSPECT_MESSAGE] = respond_to_inspect_message
pico.message_responders[LED_ON_MESSAGE] = respond_to_led_on
pico.message_responders[LED_OFF_MESSAGE] = respond_to_led_off
pico.message_responders[LED_BLINK_MESSAGE] = respond_to_led_blink


# ********************************************************************************
# Standard request methods for all nodes
# ********************************************************************************
async def send_light_on_off_message(node, state):
    await pico.send_message(node, "GET", b"/led/%s" % state)


async def send_light_on_message(node):
    await send_light_on_off_message(node, "on")


async def send_light_off_message(node):
    await send_light_on_off_message(node, "off")


async def send_light_blink_message(node):
    await send_light_on_off_message(node, "blink")


# ********************************************************************************
# Standard response handlers for endpoints.
# ********************************************************************************
async def respond_to_alive_message(method, request, headers, response_headers):
    if config.logging: print("Responding to alive message.")
    response_headers[HEADER_CONTENT_TYPE] = CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = ALIVE_RESPONSE_YES
    return response_headers[pico.HEADER_DATA]


async def respond_to_role_message(method, request, headers, response_headers):
    if config.logging: print("Responding to role message.")
    response_headers[HEADER_CONTENT_TYPE] = CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = config.role
    return response_headers[pico.HEADER_DATA]


async def respond_to_name_message(method, request, headers, response_headers):
    if config.logging: print("Responding to name message.")
    response_headers[HEADER_CONTENT_TYPE] = CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = config.name
    return response_headers[pico.HEADER_DATA]


async def respond_to_restart_message(method, request, headers, response_headers):
    if config.logging: print("Responding to restart message.")
    response_headers[HEADER_CONTENT_TYPE] = CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = RESTART_RESPONSE_YES
    asyncio.create_task(restart_node(5))

    return response_headers[pico.HEADER_DATA]


async def respond_to_register_self_message(method, request, headers, response_headers):
    if config.logging: print("Responding to register self message.")
    response_headers[HEADER_CONTENT_TYPE] = CONTENT_TYPE_PLAIN
    if config.coordinator is not None:
        await send_register_message(config.coordinator)
        response_headers[pico.HEADER_DATA] = REGISTER_RESPONSE_YES
    else:
        response_headers[pico.HEADER_DATA] = REGISTER_RESPONSE_NO

    return response_headers[pico.HEADER_DATA]


async def respond_to_unregister_self_message(method, request, headers, response_headers):
    if config.logging: print("Responding to unregister self message.")
    response_headers[HEADER_CONTENT_TYPE] = CONTENT_TYPE_PLAIN
    if config.coordinator is not None:
        await send_unregister_message(config.coordinator)
        response_headers[pico.HEADER_DATA] = UNREGISTER_RESPONSE_YES
    else:
        response_headers[pico.HEADER_DATA] = UNREGISTER_RESPONSE_NO

    return response_headers[pico.HEADER_DATA]


pico.message_responders[ALIVE_MESSAGE] = respond_to_alive_message
pico.message_responders[ROLE_MESSAGE] = respond_to_role_message
pico.message_responders[NAME_MESSAGE] = respond_to_name_message
pico.message_responders[RESTART_MESSAGE] = respond_to_restart_message
pico.message_responders[REGISTER_SELF_MESSAGE] = respond_to_register_self_message
pico.message_responders[UNREGISTER_SELF_MESSAGE] = respond_to_unregister_self_message


# ********************************************************************************
# Standard request methods to send to an endpoint.
# ********************************************************************************
async def send_alive_message(ip):
    if config.logging: print("Sending alive message to %s." % ip)
    headers = await pico.send_message(ip, "GET", ALIVE_MESSAGE)
    alive = headers[pico.HEADER_DATA]
    if config.logging: print("Alive response for %s is %s." % (ip, alive))
    return alive == ALIVE_RESPONSE_YES


async def send_role_message(ip):
    if config.logging: print("Sending role message to %s." % ip)
    headers = await pico.send_message(ip, "GET", ROLE_MESSAGE)
    role = headers[pico.HEADER_DATA]
    if config.logging: print("Role for %s is %s." % (ip, role))
    return role


async def send_name_message(ip):
    if config.logging: print("Sending name message to %s." % ip)
    headers = await pico.send_message(ip, "GET", NAME_MESSAGE)
    name = headers[pico.HEADER_DATA]
    if config.logging: print("Name for %s is %s." % (ip, name))
    return name


async def send_restart_message(ip):
    if config.logging: print("Sending restart message to %s." % ip)
    headers = await pico.send_message(ip, "GET", RESTART_MESSAGE)
    restart = headers[pico.HEADER_DATA]
    if config.logging: print("Restart response for %s is %s." % (ip, restart))
    return restart == RESTART_RESPONSE_YES


# ********************************************************************************
# Standard response handlers for coordinators.
# ********************************************************************************
async def respond_to_register_message(method, request, headers, response_headers):
    if config.logging: print("Responding to register message.")
    response_headers[HEADER_CONTENT_TYPE] = CONTENT_TYPE_PLAIN

    result = await directory.register_endpoint(
        headers[pico.HEADER_SENDER], headers[pico.HEADER_NAME], headers[pico.HEADER_ROLE])
    response_headers[pico.HEADER_DATA] = result

    return result


async def respond_to_unregister_message(method, request, headers, response_headers):
    if config.logging: print("Responding to unregister message.")
    response_headers[HEADER_CONTENT_TYPE] = CONTENT_TYPE_PLAIN

    result = await directory.unregister_endpoint(
        headers[pico.HEADER_SENDER], headers[pico.HEADER_NAME], headers[pico.HEADER_ROLE])
    response_headers[pico.HEADER_DATA] = result

    return result


async def respond_to_heartbeat_message(method, request, headers, response_headers):
    if config.logging: print("Responding to heartbeat message.")
    response_headers[HEADER_CONTENT_TYPE] = CONTENT_TYPE_PLAIN

    result = await directory.heartbeat_from_endpoint(
        headers[pico.HEADER_SENDER], headers[pico.HEADER_NAME], headers[pico.HEADER_ROLE])
    response_headers[pico.HEADER_DATA] = result

    return result


async def respond_to_lookup_all_message(method, request, headers, response_headers):
    if config.logging: print("Responding to lookup all message.")
    response_headers[HEADER_CONTENT_TYPE] = CONTENT_TYPE_PLAIN

    # This returns a dictionary of names to IPs.
    nodes = await directory.lookup_all_endpoints()
    result = ",".join(nodes.values())
    response_headers[pico.HEADER_DATA] = result

    return result


async def respond_to_lookup_name_message(method, request, headers, response_headers):
    if config.logging: print("Responding to lookup name message.")
    response_headers[HEADER_CONTENT_TYPE] = CONTENT_TYPE_PLAIN

    result = await directory.lookup_endpoint_by_name(headers[pico.HEADER_DATA])
    response_headers[pico.HEADER_DATA] = result

    return result


async def respond_to_lookup_role_message(method, request, headers, response_headers):
    if config.logging: print("Responding to lookup role message.")
    response_headers[HEADER_CONTENT_TYPE] = CONTENT_TYPE_PLAIN

    # This returns a dictionary of names to IPs.
    nodes = await directory.lookup_endpoints_by_role(headers[pico.HEADER_DATA])
    result = ",".join(nodes.values())
    response_headers[pico.HEADER_DATA] = result

    return result


pico.message_responders[REGISTER_MESSAGE] = respond_to_register_message
pico.message_responders[UNREGISTER_MESSAGE] = respond_to_unregister_message
pico.message_responders[HEARTBEAT_MESSAGE] = respond_to_heartbeat_message
pico.message_responders[LOOKUP_ALL_MESSAGE] = respond_to_lookup_all_message
pico.message_responders[LOOKUP_NAME_MESSAGE] = respond_to_lookup_name_message
pico.message_responders[LOOKUP_ROLE_MESSAGE] = respond_to_lookup_role_message


# ********************************************************************************
# Standard request methods to send to a coordinator.
# ********************************************************************************
async def send_register_message(ip):
    if config.logging: print("Sending register message to %s." % ip)
    await pico.send_message(ip, "GET", REGISTER_MESSAGE)


async def send_unregister_message(ip):
    if config.logging: print("Sending unregister message to %s." % ip)
    await pico.send_message(ip, "GET", UNREGISTER_MESSAGE)


async def send_heartbeat_message(ip):
    if config.logging: print("Sending heartbeat message to %s." % ip)
    await pico.send_message(ip, "GET", HEARTBEAT_MESSAGE)


# Returns all IP addresses registered with the coordinator, except ourselves
async def send_lookup_all_message(ip):
    if config.logging: print("Sending lookup all message to %s." % ip)
    headers = await pico.send_message(ip, "GET", LOOKUP_ALL_MESSAGE)
    all_ips = headers[pico.HEADER_DATA].split(",")
    result = []
    for ip in all_ips:
        ip = ip.strip()
        if len(ip) > 0 and ip != pico.ip:  # Remove ourselves from the list
            result.append(ip)

    if config.logging: print("All lookup return %s." % result)
    return result


# Returns the IP address registered with the coordinator with that name (does NOT exclude ourselves)

async def send_lookup_name_message(ip, name):
    if config.logging: print("Sending lookup name message to %s for %s." % (ip, name))
    headers = await pico.send_message(ip, "GET", LOOKUP_NAME_MESSAGE, name)
    name_ip = headers[pico.HEADER_DATA]
    if config.logging: print("Name %s lookup return %s." % (name, name_ip))
    return name_ip


# Returns all IP addresses registered with the coordinator for the role, except ourselves

async def send_lookup_role_message(ip, role):
    if config.logging: print("Sending lookup role message to %s for %s." % (ip, role))
    headers = await pico.send_message(ip, "GET", LOOKUP_ROLE_MESSAGE, role)
    role_ips = headers[pico.HEADER_DATA].split(",")
    result = []
    for role_ip in role_ips:
        role_ip = role_ip.strip()
        if len(role_ip) > 0 and ip != pico.ip:  # Remove ourselves from the list
            result.append(role_ip)

    if config.logging: print("Role %s lookup return %s." % (role, result))
    return result


# Registers with the coordinator and periodically runs a heartbeat message.
async def heartbeat():
    await send_register_message(config.coordinator)
    while True:
        await asyncio.sleep(60)
        await send_heartbeat_message(config.coordinator)


async def messages_task():
    if config.coordinator is not None:
        asyncio.create_task(heartbeat())


pico.messages_task = messages_task


# This is provided to make it simpler for a node as they only need to import
# messages.py. Everything else is handled from here.
def run(callback=None):
    pico.run(callback)
