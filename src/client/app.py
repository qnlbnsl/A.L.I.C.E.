import asyncio
import json
from multiprocessing import Process, Queue
import sys
import numpy as np
import time
import traceback

import websockets
from websockets.sync.client import connect

import sounddevice as sd

from encoder import encode_audio
from beamforming import beamform_audio
from led_control import clear_leds, retry_connection_led
from logger import logger
from enums import retry_max, retry_delay, RATE, CHANNELS, CHUNK


encoded_audio_queue = Queue()
beamformed_audio_queue = Queue()
raw_audio_queue = Queue()
# define processes
beamformer = Process(
    target=beamform_audio,
    args=(raw_audio_queue, beamformed_audio_queue),
)
encoder = Process(
    target=encode_audio,
    args=(beamformed_audio_queue, encoded_audio_queue),
)


def read_callback(in_data, _frame_count, _time_info, _status):
    raw_audio_queue.put_nowait(in_data)


async def run():
    host = "192.168.3.46"
    port = 8765
    source = 2
    retry_count = 0
    while retry_count < retry_max:
        try:
            async with websockets.connect(
                uri=f"ws://{host}:{port}",
                ping_timeout=None,
                ping_interval=None,
            ) as ws:  # type: ignore
                logger.debug("Socket connected")
                logger.debug("Starting audio stream")
                try:
                    # Start the beamformer
                    if not beamformer.is_alive():
                        beamformer.start()
                    # start the encoder
                    if not encoder.is_alive():
                        encoder.start()

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
                                await ws.send(
                                    json.dumps({"type": "audio", "data": audio_data})
                                )
                            else:
                                await asyncio.sleep(0.1)
                except websockets.exceptions.ConnectionClosed:
                    logger.error("Connection closed, attempting to reconnect...")

                except OSError as e:
                    logger.error(f"OS error: {e}, attempting to reconnect...")

                except KeyboardInterrupt:
                    clear_leds()
                    beamformer.join(timeout=10)
                    encoder.join(timeout=10)
                except Exception as e:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    logger.error(
                        f"Unexpected exception of type {exc_type}: {exc_value}"
                    )
                    logger.error("Exception traceback:")
                    traceback_lines = traceback.format_exception(
                        exc_type, exc_value, exc_traceback
                    )
                    for line in traceback_lines:
                        logger.error(line.rstrip())
                    logger.error(f"Unexpected exception: {e}")
                    logger.error("Closing socket...")
                    beamformer.terminate()
                    encoder.terminate()
                    clear_leds()
                    break  # close connection and reconnect
        # Exceptions
        except websockets.exceptions.ConnectionClosed:
            logger.error("Connection closed, attempting to reconnect...")

        except OSError as e:
            if e.errno == 22:
                logger.error("Invalid argument, attempting to reconnect...")
            elif e.errno == 9:
                logger.error("Bad file descriptor, attempting to reconnect...")
            elif e.errno == 104:
                logger.error("Connection reset by peer, attempting to reconnect...")
            elif e.errno == 111:
                logger.error("Connection refused, attempting to reconnect...")
            else:
                logger.error(f"Unknown OS error: {e}, attempting to reconnect...")
                exc_type, exc_value, exc_traceback = sys.exc_info()
                logger.error(f"Unexpected exception of type {exc_type}: {exc_value}")
                logger.error("Exception traceback:")
                traceback_lines = traceback.format_exception(
                    exc_type, exc_value, exc_traceback
                )
                for line in traceback_lines:
                    logger.error(line.rstrip())

        except Exception as e:
            logger.error(f"Unexpected exception: {e}")

        except KeyboardInterrupt:
            logger.debug("Exiting...")
            clear_leds()
            exit(0)
        retry_count += 1
        if retry_count < retry_max:
            logger.error(f"Waiting {retry_delay} seconds before retrying...")
            try:
                # Run retry loop
                # time.sleep(retry_delay)  # Delay before retrying
                retry_connection_led(retry_delay)
            except KeyboardInterrupt:
                logger.debug("Force Exiting...")
                exit(0)
            except Exception as e:
                logger.error(f"Unexpected exception: {e}")
                raise e
        else:
            logger.debug("Maximum retry attempts reached. Shutting down.")
    clear_leds()
    beamformer.terminate() if beamformer.is_alive() else beamformer.join()
    encoder.terminate() if encoder.is_alive() else encoder.join()


if __name__ == "__main__":
    asyncio.run(run())
