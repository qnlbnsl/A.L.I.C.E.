import wave
import numpy as np
import time
from numpy.typing import NDArray


def open(
    output_filename=f"sent_audio-{time.time()}.wav",
    channels=1,
    sample_rate=16000,
    sample_width=2,
) -> wave.Wave_write:
    wav_file = wave.open(output_filename, "wb")
    wav_file.setnchannels(channels)
    wav_file.setsampwidth(sample_width)
    wav_file.setframerate(sample_rate)
    return wav_file


def record(
    waveform: NDArray[np.int16] | NDArray[np.float32], wav_file: wave.Wave_write
) -> None:
    wav_file.writeframes(waveform.tobytes())


def close(wav_file: wave.Wave_write | None) -> None:
    if wav_file:
        wav_file.close()
