import time
import pyaudio

# Libraries
from audio.beamforming import delay_and_sum, calculate_delays, estimate_doa_with_music

# Enums
from enums import (
    CHUNK,
    FORMAT,
    CHANNELS,
    RATE,
    local_audio_queue,
    
)

mic = pyaudio.PyAudio()

sample_size = mic.get_sample_size(FORMAT)


def callback(in_data, frame_count, time_info, status):
    try:
        print("Callback called")  # This should print to the same console
        # Your callback logic here
        local_audio_queue.put(in_data)
        return (None, pyaudio.paContinue)
    except Exception as e:
        print(f"Exception in callback: {e}")  # This will print any exceptions to the same console
        import traceback
        traceback.print_exc()  # This will print the full traceback
        return (None, pyaudio.paAbort)  # Abort on exception


def initialize_audio():
    info = mic.get_host_api_info_by_index(0)
    num_devices = info.get("deviceCount")
    if num_devices is None:
        print("Could not fetch device count")
        exit()
    else:
        try:
            num_devices = int(num_devices)  # cast to int if possible
        except ValueError:
            print("Invalid device count received")
            exit()
        if num_devices < 1:
            print("No microphone found")
            exit()
    print("Opening Mic Stream")
    # open mic
    try:
        stream = mic.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            stream_callback=callback
        )
    except IOError as e:
        print(f"Could not open stream: {e}")
        exit()
    
    try:
        print("Starting Stream")
        stream.start_stream()
        while stream.is_active():
            print("sleeping")
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Exit Signal Recieved")
    finally:
        if stream is not None:
            stream.stop_stream()
            stream.close()
        mic.terminate()
        exit()



