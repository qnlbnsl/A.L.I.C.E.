import wave
import time


def record(audio_bytes, channels, sample_width, rate):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    outputfile_name = f"outfile-{timestamp}.wav"
    with wave.open(outputfile_name, "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(rate)
        wav_file.writeframes(audio_bytes)
        print(f"Audio saved to {outputfile_name}")
