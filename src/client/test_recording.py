import sounddevice as sd
import numpy as np
import wavio

# Parameters
sample_rate = 48000  # 160 kHz
channels = 8
duration = 10  # seconds
filename_prefix = "channel"


def record_audio():
    # Record audio
    print(f"Recording for {duration} seconds...")
    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=channels,
        device="hw:2,0",
    )
    sd.wait()  # Wait for the recording to finish
    return recording


def save_channels(recording):
    # Save each channel to a separate file
    for i in range(channels):
        channel_data = recording[:, i]
        filename = f"{filename_prefix}_{i+1}.wav"
        wavio.write(filename, channel_data, sample_rate, sampwidth=2)  # 16-bit PCM
        print(f"Channel {i+1} saved to {filename}")


def main():
    recording = record_audio()
    save_channels(recording)


if __name__ == "__main__":
    main()
