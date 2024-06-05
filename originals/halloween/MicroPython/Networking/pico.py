import config

VERSION: str = "0.2.6"

# The code in this file is MicroPython and common to both the coordinator and endpoint nodes.
import network
import time
import uasyncio as asyncio

# Constants for use in the data structure used for sending and receiving messages
HEADER_SENDER = 'Sender'  # Address of sender sending the message.
HEADER_HOST = 'Host'  # Address this message is being sent to (i.e. us).
HEADER_NAME = 'Name'  # Name of the sender.
HEADER_ROLE = 'Role'  # Role of the sender.
HEADER_DATA = 'Data'  # Data from the sender.

RESPONSE_OK = 'HTTP/1.0 200 OK'
RESPONSE_NOT_FOUND = 'HTTP/1.0 404 NOT_FOUND'

wlan = network.WLAN(network.STA_IF)
ip = None


def connect_to_network():
    global ip
    wlan.active(True)
    wlan.config(pm=0xa11140)  # Disable power-save mode
    wlan.connect(config.ssid, config.password)

    if config.logging: print('Connecting to network...')
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        if config.logging: print('Waiting for connection...')
        time.sleep(1)

    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        if config.logging: print('Connected to network. ' + config.ssid)
        status = wlan.ifconfig()
        ip = status[0]
        if config.logging: print('Network address:' + ip)


# Used to register handlers for requests.
message_responders = {}


async def extract_headers(reader):
    headers = {
        HEADER_SENDER: "",
        HEADER_HOST: "",
        HEADER_NAME: "",
        HEADER_ROLE: "",
        HEADER_DATA: "",
    }

    # Cycle through the headers, extracting the host, name and role of the response.
    while True:
        header = (await reader.readline()).decode('utf-8')
        if len(header.strip()) < 1:
            break

        header = str(header).strip()
        kvp = header.split(":")

        if len(kvp) < 2:
            if config.logging: print("Cannot process header: '%s'" % header)
            continue

        kvp[0] = kvp[0].strip().upper()
        kvp[1] = kvp[1].strip()
        if kvp[0] == HEADER_SENDER.upper(): headers[HEADER_SENDER] = kvp[1]
        if kvp[0] == HEADER_HOST.upper(): headers[HEADER_HOST] = kvp[1]
        if kvp[0] == HEADER_NAME.upper(): headers[HEADER_NAME] = kvp[1]
        if kvp[0] == HEADER_ROLE.upper(): headers[HEADER_ROLE] = kvp[1]
        if kvp[0] == HEADER_DATA.upper(): headers[HEADER_DATA] = kvp[1]

    return headers


# Returns a pre-populated dictionary containing the default headers.
def default_populated_headers(host):
    headers = {
        HEADER_SENDER: ip,
        HEADER_NAME: config.name,
        HEADER_ROLE: config.role,
    }

    if host is not None and len(host) > 0:
        headers[HEADER_HOST] = host

    return headers


async def send(writer, message, headers, body):
    if config.logging: print("Sending message: '%s'" % message)
    if config.logging: print("Sending headers: '%s'" % headers)
    if body is not None:
        if config.logging: print("Sending body: '%s'" % body)

    writer.write(message + "\r\n")
    for key, value in headers.items():
        if value is not None and len(value) > 0:
            writer.write('%s: %s\r\n' % (key, value))

    # Blank line to separate the headers from the body.
    writer.write('\r\n')

    if body is not None and len(body) > 0:
        writer.write(body)
        writer.write('\r\n')

    await writer.drain()


async def receive(reader):
    message = (await reader.readline()).decode('utf-8').strip()
    if config.logging: print("Received message: '%s'" % message)
    headers = await extract_headers(reader)
    if config.logging: print("Received headers: ", headers)

    # Ignore body content.

    return message, headers


async def receive_message(reader, writer):
    global message_responders
    try:
        # A request line looks like this: b'GET /light/off HTTP/1.1\r\n'
        if config.logging: print("Receiving request...")
        request, headers = await receive(reader)

        request_data = str(request).split(" ")
        if len(request_data) < 2:
            if config.logging: print("Cannot process request: '%s'" % request)
            return

        method = request_data[0].strip().upper()
        request = request_data[1]

        response = RESPONSE_NOT_FOUND
        response_headers = default_populated_headers(headers[HEADER_SENDER])
        response_body = None

        # Now see if we have a route to process this message.
        if request in message_responders:
            response = RESPONSE_OK
            responder = message_responders[request]
            response_body = await responder(method, request, headers, response_headers)
        
        if config.logging: print("Sending response...")
        await send(writer, response, response_headers, response_body)

    except Exception as e:
        if config.logging: print("An exception occurred receiving message '%s'!" % request)
        if config.logging: print("Exception raised: %s" % e)

    finally:
        await writer.wait_closed()


# node is the IP address to send to
# method is GET, PUT etc.
# request is the request to send.
async def send_message(node, method, request, data=None):
    reader, writer = await asyncio.open_connection(node, 80)
    try:
        # Send the request with our standard headers
        request = b"%s %s HTTP/1.1" % (method, request)
        request_headers = default_populated_headers(node)
        request_body = None

        if data is not None:
            request_headers[HEADER_DATA] = data

        if config.logging: print("Sending request...")
        await send(writer, request, request_headers, request_body)

        # A response looks like this: HTTP/1.0 200 OK
        if config.logging: print("Receiving response...")
        response, headers = await receive(reader)

        return headers

    except:
        if config.logging: print("An exception occurred sending message '%s'!" % request)

    finally:
        reader.close()
        await reader.wait_closed()
        writer.close()
        await writer.wait_closed()


directory_task = None  # This is a hook to allow the directory file to define a regular schedule task.
messages_task = None  # This is a hook to allow the messages file to define a regular schedule task.
user_task = None  # This is a hook to allow the user code file to define a regular schedule task.


async def main_loop():
    global directory_task, messages_task, user_task
    asyncio.create_task(asyncio.start_server(receive_message, ip, 80))

    # If a directory_task has been defined then execute it now.
    if directory_task is not None:
        asyncio.create_task(directory_task())

    # If a messages_task has been defined then execute it now.
    if messages_task is not None:
        asyncio.create_task(messages_task())

    # If a user_task has been defined then execute it now.
    if user_task is not None:
        asyncio.create_task(user_task())

    while True:
        await asyncio.sleep(10)


# A callback function can be provided which is called after initialisation
# and this can be used to schedule the clients background tasks. The callback
# needs to be in the form of 'async def name()`.
def run(callback=None):
    global user_task
    user_task = callback
    connect_to_network()
    try:
        asyncio.run(main_loop())
    finally:
        asyncio.new_event_loop()
