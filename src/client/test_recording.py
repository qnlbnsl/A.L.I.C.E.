import sounddevice as sd
import numpy as np
import queue
import threading
import wave
from logger import logger

# Define a queue to hold the audio data
audio_queue = queue.Queue()

# Parameters for the WAV file
filename = "output.wav"
channels = 8
sampwidth = 2  # width in bytes, for int16, it's 2 bytes
framerate = 16000
format = np.int16  # Assuming the callback receives int16 (PCM) data

# Open a WAV file in write mode
wav_file = wave.open(filename, "wb")
wav_file.setnchannels(channels)
wav_file.setsampwidth(sampwidth)
wav_file.setframerate(framerate)


# This function will run in a separate thread
def process_audio():
    while True:
        data = audio_queue.get()
        if data is None:
            break  # Stop the thread if None is enqueued
        # Write audio data to the WAV file
        wav_file.writeframes(data.tobytes())
        print(".", end="", flush=True)  # Just to show it's running, without flooding


def callback(indata, frames, time, status):
    logger.debug("callback: indata.shape = %s frames = %s", indata.shape, frames)
    if status.input_overflow:
        logger.error("Input overflow!")
    audio_queue.put(indata.copy(), False)  # Enqueue audio data for processing


# Start the processing thread
processing_thread = threading.Thread(target=process_audio)
processing_thread.start()

# Open an input stream with the callback function
try:
    with sd.InputStream(
        callback=callback,
        channels=channels,
        samplerate=framerate,
        blocksize=480,
        dtype=format,
        device=2,
    ):
        logger.debug("Starting stream, press Ctrl+C to stop")
        # Loop indefinitely until Ctrl+C is pressed
        while True:
            logger.debug("main thread sleeping")
            sd.sleep(100)  # Short sleep to yield control
except KeyboardInterrupt:
    logger.debug("\nRecording stopped")
except Exception as e:
    logger.error(str(e))
finally:
    audio_queue.put(None)  # Signal the processing thread to terminate
    processing_thread.join()
    wav_file.close()  # Make sure to close the file properly
    logger.debug("WAV file written")
