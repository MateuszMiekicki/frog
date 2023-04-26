import asyncio
import websockets
import time


async def get_data():
    async with websockets.connect('ws://127.0.0.1:8000/data') as websocket:
        while True:
            start_time = time.time()
            data = await websocket.recv()
            end_time = time.time()
            print(f"Time elapsed: {end_time - start_time} seconds")


async def run_multiple_connections():
    tasks = []
    for i in range(100):
        tasks.append(asyncio.ensure_future(get_data()))
    await asyncio.gather(*tasks)

asyncio.run(run_multiple_connections())
