from collections import deque
import wave
import numpy as np

import time

# Libraries
from audio.beamforming import delay_and_sum, calculate_delays, estimate_doa_with_music

from audio.capture import sample_size
# Enums
from enums import (
    mic_positions,
    CHUNK,
    FORMAT,
    CHANNELS,
    RATE,
    RECORD,
    NO_SPEECH_COUNT,
    NO_SPEECH_LIMIT,
    MIN_SPEECH_COUNT,
    DECAY,
    local_audio_queue,
    stream_queue
)

# Types
from webrtcvad import Vad

def process_audio(vad: Vad):
    global NO_SPEECH_COUNT  # only needed as we are updating the variable
    # Debug counter for number of voice detections
    count = 0

    # initialize the DoA Angles
    theta = 0
    phi = 0

    # for smoothing the VAD results
    vad_results = deque(maxlen=10)

    # initialize the buffer
    print("* recording")
    BUFFER = []
    OG_BUFFER = []
    smoothed_vad = 0.0
    while True:
        print("Checking data")
        data = local_audio_queue.get()
        print(data)
        # This comes in as a 1D array of 16bytes.
        audio_data = np.frombuffer(data, dtype=np.int16)
        # Reshape audio to an array of [CHANNEL][CHUNK]. This way each chunk is it's own channel.
        reshaped_audio_data = np.reshape(
            audio_data, (CHUNK, CHANNELS)
        ).T  # shape will be (8, 2048)
        # print(reshaped_audio_data.shape)  # Should print (8, 2048)
        assert reshaped_audio_data.shape[0] == CHANNELS
        assert reshaped_audio_data.shape[1] == CHUNK

        is_speech_flag = is_speech(audio_data=audio_data, vad=vad)
        vad_results.append(is_speech_flag)

        # Smoothing Algorithm
        smoothed_vad = DECAY * smoothed_vad + (1 - DECAY) * is_speech_flag
        # Check if it contains speech
        print(smoothed_vad)
        
        if smoothed_vad > 0.2:
            print("Speech Detected ", count, " times")
            count += 1
            # reset No Speech counter
            NO_SPEECH_COUNT = 0
            # Perform beamforming

            # Direction of interest
            theta, phi = estimate_doa_with_music(
                reshaped_audio_data, mic_positions, RATE
            )

            # Calculate delays in terms of samples rather than seconds.
            delays = calculate_delays(mic_positions, theta, phi, 343, RATE)
            beamformed_audio = delay_and_sum(
                reshaped_audio_data, delays, RATE
            )  
            BUFFER.extend(beamformed_audio)
            OG_BUFFER.extend(audio_data) # ensure that 2D Array is not passed. 
        else:
            print("No Speech")
            NO_SPEECH_COUNT += 1
            if NO_SPEECH_COUNT >= NO_SPEECH_LIMIT:
                print("No speech detected for 2 seconds")
                if len(BUFFER) > 0:
                    if count >= MIN_SPEECH_COUNT:
                        audio_chunk = np.array(BUFFER, dtype=np.int16)
                        if audio_chunk is None:
                            print("Could not convert audio to bytes")
                            continue
                        duration = len(BUFFER) / RATE  # Time in seconds
                        # Add data to queue
                        print("Size before sending:", len(audio_chunk))
                        print("shape of audio chunk: ", audio_chunk.shape)
                        stream_queue.put(
                            {
                                "AudioData": audio_chunk.tobytes(),
                                "duration": duration,
                                "theta": theta,
                                "phi": phi,
                                "channels": CHANNELS,
                                "sample_width": sample_size,
                                "rate": RATE,
                            }
                        )
                        if RECORD:
                            record_beamformed(
                                audio_chunk.tobytes(),
                                sample_size,
                            )
                            record(
                                np.array(OG_BUFFER, dtype=np.int16).tobytes(),
                                sample_size,
                            )
                    else:
                        print("Speech too short")
                    BUFFER.clear()
                    OG_BUFFER.clear()
                    count = 0
                NO_SPEECH_COUNT = 0
            # else:
            #     # Was speech??
            #     BUFFER.append()


def record(audio_chunk, sample_width):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    outputfile_name = f"outfile-{timestamp}.wav"
    with wave.open(outputfile_name, "wb") as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(RATE)
        wav_file.writeframes(audio_chunk)  # Directly write audio_chunk
        wav_file.close()

def record_beamformed(audio_chunk, sample_width, filename_suffix="beamformed"):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    outputfile_name = f"{filename_suffix}-{timestamp}.wav"
    with wave.open(outputfile_name, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(RATE)
        wav_file.writeframes(audio_chunk)  # Directly write audio_chunk
        wav_file.close()

def is_speech(audio_data, vad: Vad):
    mono_audio_data = np.mean(np.reshape(audio_data, (CHANNELS, -1)), axis=0)
    return vad.is_speech(
        buf=mono_audio_data.astype(np.int16).tobytes(), sample_rate=RATE
    )
