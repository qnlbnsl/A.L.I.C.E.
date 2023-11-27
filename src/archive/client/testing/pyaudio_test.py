import pyaudio as pa
import asyncio

# import numpy as np

# from logger import logger

py = pa.PyAudio()
device = 2
audio_queue = asyncio.Queue()

i = 0


def read_callback(in_data, frame_count, time_info, status):
    global i
    print(f"In read_callback {i}")
    audio_queue.put_nowait(in_data)
    i += 1
    return (None, pa.paContinue)


stream = py.open(
    format=pa.paInt16,
    channels=8,
    rate=16000,
    input=True,
    frames_per_buffer=640 * 8,
    stream_callback=read_callback,
    input_device_index=device if isinstance(device, int) else None,
)

try:
    stream.start_stream()
    while True:
        pass
except KeyboardInterrupt:
    stream.stop_stream()
    stream.close()
    py.terminate()
