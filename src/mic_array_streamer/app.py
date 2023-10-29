import pyaudio
import wave
import numpy as np
from beamforming import delay_and_sum, calculate_delays, estimate_doa_with_music
from webrtc import is_speech, send_to_server
from enums import CHUNK, FORMAT, CHANNELS, RECORD_SECONDS, RATE, mic_positions
# create & configure microphone
mic = pyaudio.PyAudio()
stream = mic.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

frames = []
count = 0
try:
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    # while True:
        data = stream.read(CHUNK)
        audio_data = np.frombuffer(data, dtype=np.int16)
        reshaped_audio_data = np.reshape(audio_data, (CHUNK, CHANNELS)).T  # shape will be (8, 2048)
        # print(reshaped_audio_data.shape)  # Should print (8, 2048)
        assert reshaped_audio_data.shape[0] == CHANNELS
        assert reshaped_audio_data.shape[1] == CHUNK

        # Check if it contains speech
        mono_audio_data = np.mean(np.reshape(audio_data, (CHANNELS, -1)), axis=0)
        if is_speech(mono_audio_data.astype(np.int16).tobytes(), RATE):
        # if is_speech(data, RATE):
            # Perform beamforming
            # Direction of interest
            print("Speech Detected", count)
            count = count + 1
            theta, phi = estimate_doa_with_music(reshaped_audio_data, mic_positions, RATE)

            # Calculate delays
            delays = calculate_delays(mic_positions, theta, phi)
            beamformed_audio = delay_and_sum([audio_data], delays)  # You'd have multi-channel data in a real scenario
            
            # Send to server
            send_to_server(beamformed_audio)

        frames.append(data)

    outputFile = wave.open("output.wav", 'wb')
    outputFile.setnchannels(CHANNELS)
    outputFile.setsampwidth(mic.get_sample_size(FORMAT))
    outputFile.setframerate(RATE)
    outputFile.writeframes(b''.join(frames))
    outputFile.close()
except KeyboardInterrupt:
    print("Exit Signal Recieved")
    stream.close()
    mic.terminate()
    exit()