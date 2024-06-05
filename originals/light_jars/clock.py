import asyncio
import copy
from network import requests
import time

__clock: time.struct_time = None


def get_clock() -> time.struct_time:
    global __clock
    return copy.copy(__clock)


async def execute():
    async def get_time():
        global __clock

        # This returns the seconds since the epoch.
        TIME_URL = "https://io.adafruit.com/api/v2/time/seconds"
        while True:
            # Just get the time from epoch, this it the fallback.
            local_clock = time.localtime(time.time())
            print(f"Local clock: {local_clock.tm_hour:02}:{local_clock.tm_min:02}:{local_clock.tm_sec:02}")
            clock_to_use = local_clock

            try:
                response = requests.get(TIME_URL)
                remote_clock = time.localtime(int(response.text))
                print(f"Remote clock: {remote_clock.tm_hour:02}:{remote_clock.tm_min:02}:{remote_clock.tm_sec:02}")
                clock_to_use = remote_clock
            except:
                pass

            __clock = clock_to_use

            # Update it every 2 minutes
            await asyncio.sleep(2*60)

    tasks: list[asyncio.Task] = [asyncio.create_task(get_time())]

    await asyncio.gather(*tasks)
