import asyncio


def execute(coro):
    loop = asyncio.get_event_loop()
    rs = loop.run_until_complete(coro)
    return rs
