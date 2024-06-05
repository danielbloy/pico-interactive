import asyncio


async def execute():
    async def my_task():
        while True:
            await asyncio.sleep(5*60)

    tasks: list[asyncio.Task] = [asyncio.create_task(my_task())]

    await asyncio.gather(*tasks)
