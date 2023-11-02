import time
import pyaudio
import wave

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


def initialize_audio_file(file_path):
    # Open the audio file
    wf = wave.open(file_path, 'rb')

    # Instantiate PyAudio
    p = pyaudio.PyAudio()

    # # Define callback function to stream audio chunks
    # def callback(in_data, frame_count, time_info, status):
    #     data = wf.readframes(frame_count)
    #     return (data, pyaudio.paContinue)

    # Open stream using callback
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    stream_callback=callback)
    print("starting stream")
    # Start the stream
    stream.start_stream()

    # Keep the stream active and play audio on repeat
    try:
        while stream.is_active():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exit Signal Received")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()

    # Close PyAudio
    p.terminate()

    # Close the audio file
    wf.close()