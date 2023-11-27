import json
import websockets
import asyncio
from multiprocessing import Queue
from logger import logger


def send_audio(ws: websockets.WebSocketClientProtocol, encoded_audio_queue: Queue):
    while True:
        # logger.debug("Getting audio data from queue")
        audio_data = encoded_audio_queue.get(block=True, timeout=None)
        logger.debug(f"Sending audio data to server with len: {len(audio_data)}")

        asyncio.run(ws.send(json.dumps({"type": "audio", "data": audio_data})))
        # logger.debug("Audio data sent to server")
