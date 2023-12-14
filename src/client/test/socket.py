import websockets
import asyncio


async def hello():
    uri = "ws://192.168.3.46:8765"
    async with websockets.connect(uri) as websocket:
        await websocket.send("Hello world!")
        await websocket.recv()


asyncio.get_event_loop().run_until_complete(hello())
