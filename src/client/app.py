import asyncio
import json
from multiprocessing import Process, Queue
import sys
import numpy as np
import time
import traceback

import websockets
from websockets.sync.client import connect
from audio.mic import mic

import sounddevice as sd

from audio.encoder import encode_audio
from audio.beamforming import beamform_audio
from utils.led_control import clear_leds, retry_connection_led

from utils.record import open, record, close
from logger import logger
from enums import retry_max, retry_delay, RATE, CHANNELS, CHUNK, RECORD, BLOCK_DURATION

wav_file_output, wav_file_input = None, None
file_name = time.time()
if RECORD:
    wav_file_output = open(f"recordings/output/{file_name}.wav")
    wav_file_input = open(f"recordings/input/{file_name}.wav", 8)

encoded_audio_queue = Queue()
beamformed_audio_queue = Queue()
raw_audio_queue = Queue()
received_audio_queue = Queue()
far_field_queue = Queue()
# define processes
beamformer = Process(
    target=beamform_audio,
    args=(raw_audio_queue, beamformed_audio_queue, far_field_queue),
)
encoder = Process(
    target=encode_audio,
    args=(beamformed_audio_queue, encoded_audio_queue, wav_file_output),
)


def read_callback(in_data, _frame_count, _time_info, _status):
    raw_audio_queue.put(in_data.copy())
    if wav_file_input:
        record(in_data, wav_file_input)


def playback_callback(out_data, _frame_count, _time_info, _status):
    try:
        audio_data = far_field_queue.get()
        out_data[:] = audio_data
    except Exception as e:
        logger.error(f"Error in getting audio data: {e}")
        return
    return out_data, sd.CallbackStop


def run():
    host = "192.168.3.46"
    port = 8765
    source = 2
    retry_count = 0
    audio_capture_process: Process | None = None
    audio_playback_process: Process | None = None
    stream = sd.InputStream(
        device=source,
        channels=CHANNELS,
        samplerate=RATE,
        callback=read_callback,
        dtype=np.int16,
        blocksize=CHUNK,
    )
    playback = sd.OutputStream(
        device=2,
        channels=CHANNELS,
        samplerate=RATE,
        dtype=np.int16,
        blocksize=CHUNK,
        callback=playback_callback,
    )

    while retry_count < retry_max:
        try:
            with connect(uri=f"ws://{host}:{port}") as ws:  # type: ignore
                logger.debug("Socket connected")
                logger.debug("Starting audio stream")
                try:
                    # Start the beamformer
                    if not beamformer.is_alive():
                        beamformer.start()
                    # start the encoder
                    if not encoder.is_alive():
                        encoder.start()

                except websockets.exceptions.ConnectionClosed:
                    logger.error("Connection closed, attempting to reconnect...")

                except OSError as e:
                    logger.error(f"OS error: {e}, attempting to reconnect...")

                except KeyboardInterrupt:
                    logger.debug("Exiting 1...")
                    clear_leds()
                    beamformer.join(timeout=5)
                    encoder.join(timeout=5)
                    audio_capture_process.join(timeout=5)
                    # audio_playback_process.join(timeout=5)

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
                    audio_capture_process.terminate()
                    # audio_playback_process.terminate()
                    clear_leds()
                    break  # close connection and reconnect
                finally:
                    if RECORD:
                        close(wav_file_output)
                        close(wav_file_input)
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
            logger.debug("Exiting 2...")
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
    audio_capture_process.terminate() if audio_capture_process.is_alive() else audio_capture_process.join()
    # audio_playback_process.terminate() if audio_playback_process.is_alive() else audio_playback_process.join()


if __name__ == "__main__":
    run()
    # asyncio.run(run())
