import json
import websockets

from logger import logger


def send_audio(ws: websockets.WebSocketClientProtocol, encoded_audio_queue):
    while True:
        logger.debug("Getting audio data from queue")
        audio_data = encoded_audio_queue.get()
        logger.debug("Sending audio data to server")
        ws.send(json.dumps({"type": "audio", "data": audio_data}))
        logger.debug("Audio data sent to server")
        encoded_audio_queue.task_done()
