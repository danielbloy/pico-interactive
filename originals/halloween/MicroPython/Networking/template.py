# Sample endpoint code.
import messages

import uasyncio as asyncio


# This must not be too greedy otherwise it will interfere with the HTTP server.
async def background_tasks():
    while True:
        await asyncio.sleep_ms(50)


def init():
    pass


def run():
    init()
    messages.run(background_tasks)
