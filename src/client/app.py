import asyncio
from multiprocessing import Process, Queue
import numpy as np
import time
import websockets
from pyaudio import paInt16, paContinue

from audio import get_audio_handler, open
from sender import send_audio
from encoder import encode_audio
from beamforming import beamform_audio


from logger import logger
from enums import retry_max, retry_delay, RATE, CHANNELS, CHUNK


encoded_audio_queue = Queue()
beamformed_audio_queue = Queue()
raw_audio_queue = Queue()

p = get_audio_handler()


def read_callback(in_data, frame_count, time_info, status):
    # logger.debug("Reading audio data and adding to queue")
    if status != 0:
        logger.debug(f"Status: {status}")
    # conver to numpy array
    raw_audio_queue.put_nowait(np.frombuffer(in_data, dtype=np.int16))
    return (None, paContinue)


async def run_client(host, port, source):
    # open audio source
    mic = p.open(
        format=paInt16,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        stream_callback=read_callback,
        input_device_index=source,
    )

    async with websockets.connect(f"ws://{host}:{port}") as ws:
        logger.debug("Socket connected")
        logger.debug("Starting audio stream")
        mic.start_stream()
        # Start the beamformer
        beamformer = Process(
            target=beamform_audio, args=(raw_audio_queue, beamformed_audio_queue)
        )
        # start the encoder
        encoder = Process(
            target=encode_audio, args=(beamformed_audio_queue, encoded_audio_queue)
        )
        # start the sender
        sender = Process(target=send_audio, args=(ws, encoded_audio_queue))

        try:
            beamformer.start()
            encoder.start()
            # sender.start()
            while True:
                await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            logger.debug("Exiting...")
            beamformer.join(timeout=10)
            encoder.join(timeout=10)
            # sender.join(timeout=10)
            exit(0)


async def run():
    retry_count = 0
    try:
        while retry_count < retry_max:
            try:
                await run_client(
                    "192.168.3.46",
                    "8080",
                    2,
                )
                break  # If run_client completes without exceptions, exit loop
            # Exceptions
            except websockets.exceptions.ConnectionClosed:
                logger.debug("Connection closed, attempting to reconnect...")
            except OSError as e:
                logger.debug(f"OS error: {e}, attempting to reconnect...")
            except Exception as e:
                logger.debug(f"Unexpected exception: {e}")

            retry_count += 1
            if retry_count < retry_max:
                logger.debug(f"Waiting {retry_delay} seconds before retrying...")
                time.sleep(retry_delay)  # Delay before retrying
            else:
                logger.debug("Maximum retry attempts reached. Shutting down.")
    except KeyboardInterrupt:
        logger.debug("Exiting...")
        exit(0)


if __name__ == "__main__":
    asyncio.run(run())
