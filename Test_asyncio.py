# modified fetch function with semaphore
import random
import time
import types
import asyncio
from aiohttp import ClientSession

async def fetch(url, session):
    async with session.get(url) as response:
        delay = response.headers.get("DELAY")
        date = response.headers.get("DATE")
        print("{}:{} with delay {}".format(date, response.url, delay))
        return await response.read()


async def bound_fetch(sem, url, session):
    # Getter function with semaphore.
    async with sem:
        await fetch(url, session)


async def run(r):
    url = "http://localhost:8080/{}"
    tasks = []
    # create instance of Semaphore
    sem = asyncio.Semaphore(1000)

    # Create client session that will ensure we dont open new connection
    # per each request.
    async with ClientSession() as session:
        for i in range(r):
            # pass Semaphore and session to every GET request
            task = asyncio.ensure_future(bound_fetch(sem, url.format(i), session))
            tasks.append(task)

        responses = asyncio.gather(*tasks)
        await responses

#number = 10000
#loop = asyncio.get_event_loop()

#uture = asyncio.ensure_future(run(number))
#loop.run_until_complete(future)

async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)


@types.coroutine
def __yield():
    """Skip one event loop run cycle.

    It uses a bare 'yield' expression
    (which Task.__step knows how to handle)
    instead of creating a Future object.
    """
    yield

def a(x=1, y=1, z=3, *args, **kwargs):
    print(x, y, z)
    print(args)
    print(kwargs)


async def main():
    task1 = asyncio.create_task(
        say_after(1, 'hello'))

    task2 = asyncio.create_task(
        say_after(2, 'world'))

    print(f"started at {time.strftime('%X')}")

    # Wait until both tasks are completed (should take
    # around 2 seconds.)
    #await task1
    #await task2
    #await asyncio.sleep(3)
    #print(asyncio.all_tasks())
    #while True:
    #    print(task1.done(), task2.done())
    #    if task1.done():
    #        print(task1.result())
    #    await asyncio.sleep(0.1)
    loop = asyncio.get_event_loop()
    #loop.run_until_complete()
    while not task2.done():
        await __yield()

    print(f"finished at {time.strftime('%X')}")

#loop = asyncio.events.new_event_loop()
#loop.run_forever()
#task1 = asyncio.create_task(say_after(1, 'hello'))
#task2 = asyncio.create_task(say_after(2, 'hello'))
#task3 = asyncio.create_task(say_after(3, 'hello'))

asyncio.run(main())
