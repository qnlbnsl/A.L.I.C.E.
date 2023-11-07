import pyaudio
import sounddevice as sd
import time
import numpy as np
import scipy.signal as signal

CHUNK: int = 4096
FORMAT: int = pyaudio.paInt16
CHANNELS: int = 1
RATE: int = 44100

sd.Stream()

# # Define callback function to process input audio chunks
# def callback(in_data, frame_count, time_info, status):
#     # Process the input data - for example, just print the length of the data
#     print(f"Received data of length: {len(in_data)}")
#     return (in_data, pyaudio.paContinue)
def callback(in_data, frame_count, time_info, flag):
    global b,a,fulldata #global variables for filter coefficients and array
    audio_data = np.fromstring(in_data, dtype=np.float32)
    #do whatever with data, in my case I want to hear my data filtered in realtime
    audio_data = signal.filtfilt(b,a,audio_data,padlen=200).astype(np.float32).tostring()
    fulldata = np.append(fulldata,audio_data) #saves filtered data in an array
    return (audio_data, pyaudio.paContinue)
# Initialize PyAudio
p = pyaudio.PyAudio()

# Open stream with input=True
stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            output=True,
            frames_per_buffer=CHUNK,
            stream_callback=callback
        )

# Start the stream
stream.start_stream()

# Wait for stream to be active
try:
    while stream.is_active():
        print("Reading and sleeping")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exit signal received")

# Stop and close the stream
stream.stop_stream()
stream.close()

# Terminate PyAudio
p.terminate()
