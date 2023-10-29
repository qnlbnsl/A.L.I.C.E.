import pyaudio
import numpy as np
from beamforming import delay_and_sum, calculate_delays, estimate_doa_with_music
from webrtc import is_speech, send_to_server

# recording configs
CHUNK = 2048
FORMAT = pyaudio.paInt16
CHANNELS = 8
RATE = 96000
RECORD_SECONDS = 5
# Microphone positions in millimeters, converted to meters
mic_positions = np.array([
    [20.0908795e-3, -48.5036755e-3, 0],
    [-20.0908795e-3, -48.5036755e-3, 0],
    [-48.5036755e-3, -20.0908795e-3, 0],
    [-48.5036755e-3, 20.0908795e-3, 0],
    [-20.0908795e-3, 48.5036755e-3, 0],
    [20.0908795e-3, 48.5036755e-3, 0],
    [48.5036755e-3, 20.0908795e-3, 0],
    [48.5036755e-3, -20.0908795e-3, 0]
])
# create & configure microphone
mic = pyaudio.PyAudio()
stream = mic.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

frames = []
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    audio_data = np.frombuffer(data, dtype=np.int16)
    reshaped_audio_data = np.reshape(audio_data, (CHUNK, CHANNELS)).T  # shape will be (8, 2048)
    print(reshaped_audio_data.shape)  # Should print (8, 2048)
    assert reshaped_audio_data.shape[0] == CHANNELS
    assert reshaped_audio_data.shape[1] == CHUNK

    # Check if it contains speech
    if is_speech(data, RATE):
        # Perform beamforming
        # Direction of interest
        theta, phi = estimate_doa_with_music(reshaped_audio_data, mic_positions, RATE)

        # Calculate delays
        delays = calculate_delays(mic_positions, theta, phi)
        beamformed_audio = delay_and_sum([audio_data], delays)  # You'd have multi-channel data in a real scenario
        
        # Send to server
        send_to_server(beamformed_audio)

    frames.append(data)
