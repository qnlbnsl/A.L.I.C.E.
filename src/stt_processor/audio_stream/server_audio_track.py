import asyncio
from aiortc import MediaStreamTrack

from audio_stream.media_recorder import MediaRecorder

from logger import logger


class ServerAudioTrack(MediaStreamTrack):
    kind = "audio"

    def __init__(self, recorder: MediaRecorder):
        super().__init__()  # don't forget to call super!
        self.recorder = recorder
        self.__queue = asyncio.Queue()

    async def recv(self):
        try:
            frame = await self.__queue.get()
            # Convert the frame to raw bytes and add it to the recorder's queue
            if frame:
                # If this is the first frame, start recording
                if not self.recorder.is_recording():
                    self.recorder.start_recording()
                # Convert the frame to raw bytes and add it to the recorder's queue
                self.recorder.add_frame(frame.to_bytes())
            return frame
        except Exception as e:
            logger.error(f"Error: {e}")

    async def put_frame(self, frame):
        await self.__queue.put(frame)

    # Call this method when the track ends
    def stop(self):
        super().stop()
        # Notify the recorder to stop recording
        self.recorder.stop_recording()
