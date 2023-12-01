import base64
from typing import Text
import wave
from line_profiler import profile
import numpy as np
from numpy.typing import NDArray
from multiprocessing import Queue
from pyogg import OpusEncoder, OpusDecoder  # type: ignore # Pylance issue

from logger import logger
from enums import CHUNK, RATE, BLOCK_DURATION
from record import record

# Create an Opus encoder/decoder
opus_encoder = OpusEncoder()
opus_decoder = OpusDecoder()

opus_encoder.set_application("audio")  # type: ignore

opus_encoder.set_sampling_frequency(RATE)  # type: ignore
opus_decoder.set_sampling_frequency(RATE)  # type: ignore

opus_encoder.set_channels(1)  # type: ignore
opus_decoder.set_channels(1)  # type: ignore


def encode_audio(
    beamformed_audio_queue: Queue,
    encoded_audio_queue: Queue,
    wav_file: wave.Wave_write | None = None,
) -> None:
    while True:
        audio_data = beamformed_audio_queue.get()
        # convert to np.int16
        if wav_file:
            record(audio_data, wav_file)
        audio_data = audio_data.astype(np.int16)
        encoded_audio = encode(audio_data)
        encoded_audio_queue.put(encoded_audio)


@profile
def encode(waveform: NDArray[np.int16]) -> Text | None:
    try:
        # Ensure waveform is in int16 format and convert to bytes
        byte_audio = waveform.tobytes()
        # Ensure the audio is the correct length
        assert calculate_sample_duration(byte_audio) == BLOCK_DURATION
        # Encode the audio
        encoded_audio = opus_encoder.encode(byte_audio)  # type: ignore
        return base64.b64encode(encoded_audio).decode("utf-8")
    except Exception as e:
        logger.error(f"Error in Opus encoding: {type(e).__name__}, {e}")
        return None  # Or handle the error as appropriate


def decode(data: Text) -> NDArray[np.int16]:
    # Decode chunk encoded in base64
    byte_samples = base64.decodebytes(data.encode("utf-8"))
    # Recover array from bytes
    samples = np.frombuffer(byte_samples, dtype=np.int16)
    return samples.reshape(1, -1)


def calculate_sample_duration(pcm: bytes) -> int:
    bytes_per_sample = 2
    channels = 1
    frame_size = len(pcm) // bytes_per_sample // channels  # bytes
    frame_duration = (10 * frame_size) // (RATE // 1000)
    return frame_duration // 10
