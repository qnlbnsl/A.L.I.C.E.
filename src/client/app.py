import asyncio
from multiprocessing import Process, Queue
import numpy as np
import time
import websockets
import sounddevice as sd
from pyaudio import paInt16, paContinue


from sender import send_audio
from encoder import encode_audio
from beamforming import beamform_audio
from led_control import clear_leds

from logger import logger
from enums import retry_max, retry_delay, RATE, CHANNELS, CHUNK


encoded_audio_queue = Queue()
beamformed_audio_queue = Queue()
raw_audio_queue = Queue()



def read_callback(in_data, frame_count, time_info, status):
    raw_audio_queue.put_nowait(in_data)


async def run_client(host, port, source):
    async with websockets.connect(f"ws://{host}:{port}") as ws:
        logger.debug("Socket connected")
        logger.debug("Starting audio stream")

        # define processes
        beamformer = Process(
            target=beamform_audio, args=(raw_audio_queue, beamformed_audio_queue)
        )
        encoder = Process(
            target=encode_audio, args=(beamformed_audio_queue, encoded_audio_queue)
        )
        sender = Process(target=send_audio, args=(ws, encoded_audio_queue))

        try:
            # Start the beamformer
            beamformer.start()
            # start the encoder
            encoder.start()
            # start the sender
            sender.start()
            with sd.InputStream(
                device=source,
                channels=CHANNELS,
                samplerate=RATE,
                callback=read_callback,
                dtype=np.int16,
                blocksize=CHUNK,
            ):
                while True:
                    await asyncio.sleep(1)
                # makes pylance happy
                return True
        except KeyboardInterrupt:
            logger.debug("Exiting...")
            clear_leds()
            beamformer.join(timeout=10)
            encoder.join(timeout=10)
            sender.join(timeout=10)
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
