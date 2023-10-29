import pyaudio
import wave
import asyncio
import numpy as np
import webrtcvad

# Libraries
from beamforming import delay_and_sum, calculate_delays, estimate_doa_with_music
from webrtc import send_to_server, init_connection

# Enums
from enums import CHUNK, FORMAT, CHANNELS, RECORD_SECONDS, RATE, RECORD, mic_positions

# create & configure microphone
mic = pyaudio.PyAudio()
# Create and configure Voice Activity Detection
vad = webrtcvad.Vad(3)

# open mic
stream = mic.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
frames = []
async def main():
    try:
        # Create an event loop and run the send_to_server coroutine
        loop = asyncio.get_event_loop()
        print("connecting to server")
        await init_connection()
        count = 0
        # for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        while True:
            print("* recording")
            data = stream.read(CHUNK)
            audio_data = np.frombuffer(data, dtype=np.int16)
            reshaped_audio_data = np.reshape(audio_data, (CHUNK, CHANNELS)).T  # shape will be (8, 2048)
            # print(reshaped_audio_data.shape)  # Should print (8, 2048)
            assert reshaped_audio_data.shape[0] == CHANNELS
            assert reshaped_audio_data.shape[1] == CHUNK

            # Check if it contains speech
            mono_audio_data = np.mean(np.reshape(audio_data, (CHANNELS, -1)), axis=0)
            if vad.is_speech(buf=mono_audio_data.astype(np.int16).tobytes(), sample_rate=RATE):
                print("Speech Detected", count)
                count = count + 1
                # Perform beamforming
                # Direction of interest
                theta, phi = estimate_doa_with_music(reshaped_audio_data, mic_positions, RATE)

                # Calculate delays
                delays = calculate_delays(mic_positions, theta, phi)
                beamformed_audio = delay_and_sum([audio_data], delays)  # You'd have multi-channel data in a real scenario
                
                # Send to server
                # send_to_server()
                loop.run_until_complete(send_to_server(beamformed_audio, theta, phi))
            if RECORD:
                frames.append(data)

    except KeyboardInterrupt:
        print("Exit Signal Recieved")
        stream.close()
        mic.terminate()
        print("Record was set to: ", RECORD)
        if RECORD:
            outputFile = wave.open("output.wav", 'wb')
            outputFile.setnchannels(CHANNELS)
            outputFile.setsampwidth(mic.get_sample_size(FORMAT))
            outputFile.setframerate(RATE)
            outputFile.writeframes(b''.join(frames))
            outputFile.close()
        exit()

if __name__ == "__main__":
    asyncio.run(main())