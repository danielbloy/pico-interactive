import config
import pico

VERSION: str = "0.2.4"

import uasyncio as asyncio

import time


# Maps names to IP address and role.
directory = {}

IP = "ip"
ROLE = "role"
EXPIRE = "expire"


async def register_endpoint(ip, name, role):
    global directory
    expiry = time.time() + 120
    name = name.strip()
    if len(name) <= 0:
        return ''

    directory[name] = {IP: ip.strip(), ROLE: role.strip(), EXPIRE: expiry}
    return 'Registered'


async def unregister_endpoint(ip, name, role):
    global directory
    name = name.strip()
    if len(name) <= 0:
        return ''

    if name not in directory:
        return 'Unknown'

    del directory[name]
    return 'Unregistered'


async def heartbeat_from_endpoint(ip, name, role):
    await register_endpoint(ip, name, role)
    return 'Heartbeat'


# Returns the IP address for all the known nodes
async def lookup_all_endpoints():
    global directory
    return dict((name, value[IP]) for name, value in directory.items())


# Returns the IP address for the first matching name
async def lookup_endpoint_by_name(name):
    global directory
    name = name.strip()

    if name not in directory:
        return ''

    return directory[name][IP]


# Return a dictionary of names to IPs.
async def lookup_endpoints_by_role(role):
    global directory
    return dict((name, value[IP]) for name, value in directory.items() if value[ROLE] == role)


# Periodically look into the set of registered nodes and look for expired endpoints.
async def expire_endpoints():
    global directory
    while True:
        await asyncio.sleep(120)
        if config.logging: print("Checking for endpoint expiration.")
        now = time.time()
        to_remove = []
        for name, value in directory.items():
            if value[EXPIRE] < now:
                to_remove.append(name)

        for name in to_remove:
            del directory[name]


async def directory_task():
    asyncio.create_task(expire_endpoints())


pico.directory_task = directory_task
