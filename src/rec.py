import numpy as np
import sounddevice as sd
import wave
import matplotlib.pyplot as plt
from queue import Queue

# Configuration
CHANNELS = 8
RATE = 16000
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"
CHUNK = int(RATE * RECORD_SECONDS / CHANNELS)  # Adjust CHUNK as needed

# Initialize Queue
audio_queue = Queue()


# Callback function to collect audio data
def callback(in_data, frame_count, time_info, status):
    if status:
        print(status)
    audio_queue.put(in_data)


# Function to record audio and save to WAV file
def record_audio(queue, channels, rate, filename, duration):
    with sd.InputStream(channels=channels, samplerate=rate, callback=callback):
        sd.sleep(int(duration * 1000))  # Recording duration in milliseconds
    print("* Done recording")

    # Save to WAV file
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 2 bytes for int16
        wf.setframerate(rate)
        while not queue.empty():
            wf.writeframes(queue.get())


# Record audio
record_audio(audio_queue, CHANNELS, RATE, WAVE_OUTPUT_FILENAME, RECORD_SECONDS)

# Read the WAV file and create the comparison plots
with wave.open(WAVE_OUTPUT_FILENAME, "rb") as wf:
    original_audio_data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)

# Reshape the audio data from interleaved to separate channels
reshaped_audio_data = np.reshape(original_audio_data, (CHANNELS, CHUNK), order="C")

# Re-interleave the audio data from the separate channels
reinterleaved_audio_data = np.ravel(reshaped_audio_data, order="F")


# Plot and compare waveforms
def plot_comparison(original, reshaped, reinterleaved, channels):
    fig, axs = plt.subplots(3, 1, figsize=(15, 9), sharex=True)

    # Original
    axs[0].plot(original, label="Original", alpha=0.5)
    axs[0].set_title("Original Audio")
    axs[0].legend()

    # Reshaped (plot a part of each channel for clarity)
    for i in range(channels):
        axs[1].plot(
            reshaped[i, :1000], label=f"Channel {i+1}", alpha=0.5
        )  # Plot first 1000 samples for clarity
    axs[1].set_title("Reshaped Audio")
    axs[1].legend()

    # Reinterleaved
    axs[2].plot(
        reinterleaved[: channels * 1000], label="Reinterleaved", alpha=0.5
    )  # Plot first 1000 samples of each channel for clarity
    axs[2].set_title("Reinterleaved Audio")
    axs[2].legend()

    plt.tight_layout()
    plt.savefig("audio_comparison.png")
    plt.close()


plot_comparison(
    original_audio_data, reshaped_audio_data, reinterleaved_audio_data, CHANNELS
)
