import asyncio
from aiortc import MediaStreamTrack


# This will be our audio track which will receive audio from the client
class ServerAudioTrack(MediaStreamTrack):
    kind = "audio"

    def __init__(self):
        super().__init__()  # don't forget to call super!
        self.__queue = asyncio.Queue()

    async def recv(self):
        frame = await self.__queue.get()
        return frame

    async def put_frame(self, frame):
        await self.__queue.put(frame)
