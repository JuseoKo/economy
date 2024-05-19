import asyncio
import random

li = []
async def prin(i):
    await asyncio.sleep(random.random())
    li.append(i)

async def main():
    tasks = []
    for i in range(10):
        task = asyncio.create_task(prin(i))
        tasks.append(task)

    await asyncio.gather(*tasks)
    print(li)

asyncio.run(main())
