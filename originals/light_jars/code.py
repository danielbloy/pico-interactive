if __name__ == '__main__':
    import asyncio

    async def execute():
        tasks: list[asyncio.Task] = []

        import network
        tasks.append(asyncio.create_task(network.execute()))

        import clock
        tasks.append(asyncio.create_task(clock.execute()))

        import events
        tasks.append(asyncio.create_task(events.execute()))

        import pixels
        tasks.append(asyncio.create_task(pixels.execute()))

        await asyncio.gather(*tasks)

    asyncio.run(execute())
