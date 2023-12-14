from multiprocessing import Queue
from websockets.sync.client import ClientConnection
import sounddevice as sd
import numpy as np
import json
from logger import logger


def response(
    received_audio_queue: Queue,
    ws: ClientConnection,
):
    while True:
        try:
            data = ws.recv()
            data = json.loads(data)
            if data["type"] == "audio":
                received_audio_queue.put(data["data"])
            else:
                logger.error(f"Unknown data type: {data['type']}")
                continue
        except Exception as e:
            logger.error(f"Error in getting audio data: {e}")
            continue
        continue


def playback(
    recieved_audio_queue: Queue,
    far_field_queue: Queue,
    RATE: int,
    CHANNELS: int,
    CHUNK: int,
    BLOCK_DURATION: float,
):
    with sd.OutputStream(
        device=2,
        channels=CHANNELS,
        samplerate=RATE,
        dtype=np.int16,
        blocksize=CHUNK,
    ):
        while True:
            try:
                audio_data = recieved_audio_queue.get()
                if len(audio_data) > 0:
                    far_field_queue.put(audio_data)
                    sd.play(audio_data)
            except Exception as e:
                logger.error(f"Error in getting audio data: {e}")
                continue
            continue
