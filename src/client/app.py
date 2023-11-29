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
from led_control import clear_leds

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
    port = 8080
    source = 2
    retry_count = 0
    while retry_count < retry_max:
        try:
            with connect(
                f"ws://{host}:{port}",
            ) as ws:
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
                                audio_data = encoded_audio_queue.get(
                                    block=True, timeout=None
                                )
                            except Exception as e:
                                logger.error(f"Error in getting audio data: {e}")
                                continue
                            # logger.debug(f"Got encoded audio data with len: {len(audio_data)}")
                            # logger.debug("Sending audio data to server")
                            if len(audio_data) > 0:
                                ws.send(
                                    json.dumps({"type": "audio", "data": audio_data})
                                )
                            else:
                                await asyncio.sleep(0.1)
                except websockets.exceptions.ConnectionClosed:
                    logger.debug("Connection closed, attempting to reconnect...")
                except OSError as e:
                    logger.debug(f"OS error: {e}, attempting to reconnect...")
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
                    logger.debug(f"Unexpected exception: {e}")
                    logger.debug("Closing socket...")
                    beamformer.terminate()
                    encoder.terminate()
                    # ws.close()
                    break  # close connection and reconnect
        # Exceptions
        except websockets.exceptions.ConnectionClosed:
            logger.debug("Connection closed, attempting to reconnect...")
        except OSError as e:
            logger.debug(f"OS error: {e}, attempting to reconnect...")
        except Exception as e:
            logger.debug(f"Unexpected exception: {e}")
        except KeyboardInterrupt:
            logger.debug("Exiting...")
            exit(0)
        retry_count += 1
        if retry_count < retry_max:
            logger.debug(f"Waiting {retry_delay} seconds before retrying...")
            try:
                time.sleep(retry_delay)  # Delay before retrying
            except KeyboardInterrupt:
                logger.debug("Force Exiting...")
                exit(0)
            except Exception as e:
                logger.debug(f"Unexpected exception: {e}")
                raise e
        else:
            logger.debug("Maximum retry attempts reached. Shutting down.")


if __name__ == "__main__":
    asyncio.run(run())
