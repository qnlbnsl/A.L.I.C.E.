import base64
from typing import Text
from line_profiler import profile
import numpy as np
from numpy.typing import NDArray

from pyogg import OpusEncoder, OpusDecoder  # type: ignore # Pylance issue

from client.logger import logger
from enums import CHUNK, RATE


# Create an Opus encoder/decoder
opus_encoder = OpusEncoder()
opus_decoder = OpusDecoder()

opus_encoder.set_application("audio")

opus_encoder.set_sampling_frequency(RATE)
opus_decoder.set_sampling_frequency(RATE)

opus_encoder.set_channels(1)
opus_decoder.set_channels(1)


@profile
def encode_audio(waveform: NDArray[np.int16]) -> Text | None:
    try:
        # Ensure waveform is in int16 format and convert to bytes
        byte_audio = waveform.tobytes()
        # byte_audio = bytes(waveform)
        encoded_audio = opus_encoder.encode(byte_audio)
        return base64.b64encode(encoded_audio).decode("utf-8")

    except Exception as e:
        logger.error(f"Error in Opus encoding: {type(e).__name__}, {e}")
        return None  # Or handle the error as appropriate


def decode_audio(data: Text) -> NDArray[np.int16]:
    # Decode chunk encoded in base64
    byte_samples = base64.decodebytes(data.encode("utf-8"))
    # Recover array from bytes
    samples = np.frombuffer(byte_samples, dtype=np.int16)
    return samples.reshape(1, -1)
