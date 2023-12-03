from multiprocessing import Queue
import numpy as np
import asyncio
from logger import logger

# from enums import RATE, mic_positions
from audio_processing.beamforming import beamform_audio

prepped_audio_queue = Queue()

raw_audio_queue: Queue[bytes] = Queue()

BEAMFORM = False


async def process_audio():
    # initialize the buffer
    logger.debug("Starting Audio Processing")
    while True:
        # print("Checking data")

        data = raw_audio_queue.get()

        # print(data)
        # This comes in as a 1D array of 16bytes.
        audio_data = np.frombuffer(data, dtype=np.int16)

        if BEAMFORM:
            try:
                prepped_audio = beamform_audio(audio_data=audio_data)
            except Exception as e:
                logger.error(f"Error in beamforming: {e}")
                prepped_audio = audio_data
        else:
            prepped_audio = audio_data
        # prepped_audio = beamform_audio(audio_data=audio_data)
        # logger.debug(f"Received audio data of shape: {prepped_audio.shape}")
        prepped_audio_queue.put(prepped_audio)
