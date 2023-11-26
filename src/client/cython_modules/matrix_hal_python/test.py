from matrix_hal_python import PyMatrixIOBus, PyMicrophoneArray

bus = PyMatrixIOBus()
mic_array = PyMicrophoneArray(bus, 16000, 5, True)  # Example: 16000 Hz, gain 5
mic_array.calculate_delays(0, 0, 1000, 320 * 1000)
# mic_array.read()
DURATION = 5  # seconds
for i in range(0, int(DURATION * 16000 / 8)):
    mic_array.read()
    audio_data = mic_array.get_audio_data(8, 640)  # For channel 0, 640 samples
    print(audio_data)
