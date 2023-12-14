from multiprocessing import Queue
from websockets.sync.client import ClientConnection
import sounddevice as sd
import numpy as np
import json
from logger import logger


def mic(
    encoded_audio_queue: Queue,
    ws: ClientConnection,
    source: int,
    RATE: int,
    CHANNELS: int,
    CHUNK: int,
    BLOCK_DURATION: float,
    read_callback,
):
    with sd.InputStream(
        device=source,
        channels=CHANNELS,
        samplerate=RATE,
        callback=read_callback,
        dtype=np.int16,
        blocksize=CHUNK,
    ):
        while True:
            try:
                audio_data = encoded_audio_queue.get()
            except Exception as e:
                logger.error(f"Error in getting audio data: {e}")
                continue
            # logger.debug(f"Got encoded audio data with len: {len(audio_data)}")
            # logger.debug("Sending audio data to server")
            if len(audio_data) > 0:
                ws.send(json.dumps({"type": "audio", "data": audio_data}))
            # else:
            #     # continue
            #     sd.sleep(
            #         BLOCK_DURATION / 2000
            #     )  # sleep for BLOCK_DURATION / 2 in ms
