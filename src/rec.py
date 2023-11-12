import time
import pyaudio
import wave

# recording configs
CHUNK = 2048
FORMAT = pyaudio.paInt16
CHANNELS = 8
RATE = 16000
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

frames = []


# Callback function to process incoming audio
def callback(in_data, frame_count, time_info, status):
    global frames
    print("callback")
    frames.append(in_data)
    return (in_data, pyaudio.paContinue)


# create & configure microphone
mic = pyaudio.PyAudio()
stream = mic.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK,
    input_device_index=2,
    stream_callback=callback,  # Set the callback function
)

stream.start_stream()

print("* recording")
while stream.is_active():
    time.sleep(0.1)  # Small delay to prevent tight loop

print("* done recording")


# # read & store microphone data per frame read
# frames = []
# for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
#     print("Recording frame: " + str(i))
#     data = stream.read(CHUNK)
#     frames.append(data)

print("* done recording")

# kill the mic and recording
stream.stop_stream()
stream.close()
mic.terminate()

# combine & store all microphone data to output.wav file
outputFile = wave.open(WAVE_OUTPUT_FILENAME, "wb")
outputFile.setnchannels(CHANNELS)
outputFile.setsampwidth(mic.get_sample_size(FORMAT))
outputFile.setframerate(RATE)
outputFile.writeframes(b"".join(frames))
outputFile.close()
