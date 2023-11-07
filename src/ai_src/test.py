import sounddevice as sd
import numpy as np
import queue
import threading

# Define a queue to hold the audio data
audio_queue = queue.Queue()

# This function will run in a separate thread
def process_audio():
    while True:
        data = audio_queue.get()
        if data is None:
            break  # Stop the thread if None is enqueued
        # Here you can process your audio data
        print(".", end="", flush=True)  # Just to show it's running, without flooding

def callback(indata, frames, time, status):
    # print("callback")
    if status.input_overflow:
        print('Input overflow!', flush=True)
    audio_queue.put(indata.copy(), False)  # Enqueue audio data for processing

# Start the processing thread
processing_thread = threading.Thread(target=process_audio)
processing_thread.start()

# Open an input stream with the callback function
try:
    device_info = sd.query_devices(2, 'input')
    sample_rate = 48000 #type:ignore
    print(sample_rate)
    with sd.InputStream(callback=callback, 
                        channels=8, 
                        samplerate=sample_rate,
                        blocksize=960,
                        dtype=np.int16,
                        device=2
                        ):
        print("Starting stream, press Ctrl+C to stop")
        sd.sleep(10000)  # Keep the stream open for a certain amount of time
except KeyboardInterrupt:
    audio_queue.put(None)  # Signal the processing thread to terminate
    processing_thread.join()
    print("\nStream stopped")
except Exception as e:
    print(str(e))
