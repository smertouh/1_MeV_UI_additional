import asyncio
from datetime import datetime


def stamp(*args):
    print(datetime.now().strftime('%X.%f'), *args)


async def switch():
    stamp('switch')


async def say_after(delay, what):
    stamp('say_after: entry', delay, what)
    await asyncio.sleep(delay)
    stamp('say_after: exit', delay, what)


async def main():
    stamp("main: started")

    task1 = asyncio.create_task(
        say_after(1, 'hello'))
    task2 = asyncio.create_task(
        say_after(2, 'world'))
    stamp("main: tasks created")

    # Wait until both tasks are completed (should take
    # around 2 seconds.)

    await switch()
    stamp("main: after await switch")
    await asyncio.sleep(0)
    stamp("main: after await asyncio.sleep(0)")

    await say_after(2.2, 'velo')
    stamp("main: after first await")
    await say_after(1.1, 'moto')

    stamp("main: finished")

asyncio.run(main())
