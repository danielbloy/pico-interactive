from environment import isRunningOnMicroController
from config import TIMEZONE as tz
import asyncio
import os
import ssl


# This file also handles secrets for network access.
AIO_USERNAME: str = ""
AIO_KEY: str = ""
TIMEZONE: str = tz

# This file allows running network code when running in CircuitPython on a Microcontroller
# or when running on a Computer with Python and using Blinka. When running on a Microcontroller,
# the CircuitPython network libraries are used to expose requests and when running on a Computer
# the Python requests library is used.

if isRunningOnMicroController:
    import wifi
    import socketpool
    import adafruit_requests

    # Connect to the WiFi and setup requests
    wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))

    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())

    AIO_USERNAME = os.getenv('AIO_USERNAME')
    AIO_KEY = os.getenv('AIO_KEY')

else:
    import requests
    import toml

    with open('settings.toml', 'r') as f:
        config = toml.load(f)

    AIO_USERNAME = config['AIO_USERNAME']
    AIO_KEY = config['AIO_KEY']


async def execute():
    async def my_task():
        await asyncio.sleep(5*60)

    tasks: list[asyncio.Task] = [asyncio.create_task(my_task())]

    await asyncio.gather(*tasks)
