import asyncio
from multiprocessing import Queue
from websockets.sync.server import serve, ServerConnection
import websockets
import base64
import json
from pyogg import OpusEncoder, OpusDecoder  # type: ignore
import numpy as np

from numpy.typing import NDArray

from logger import logger

from enums import CHUNK, RATE

# TODO: Update as per the TTS sample rate and channels
# Create an Opus encoder/decoder
opus_encoder = OpusEncoder()

# The following are exported in a very weird fashion.
# Pylance is unable to detect these functions
opus_encoder.set_application("restricted_lowdelay")  # type: ignore
opus_encoder.set_sampling_frequency(RATE)  # type: ignore
opus_encoder.set_channels(1)  # type: ignore


def decode_audio(
    encoded_data: str,
) -> NDArray[np.int16] | None:
    """
    Decode the base64 and Opus encoded audio data.
    :param encoded_data: Base64 encoded string of Opus audio data.
    :return: Decoded raw audio bytes.
    """
    # base64_data = encoded_data.encode("utf-8")
    # Decode the base64 data to get Opus encoded bytes
    opus_data = base64.b64decode(encoded_data.encode("utf-8"))
    try:
        # Then, decode the Opus bytes to get raw audio data
        # logger.debug(f"Decoding audio of length: {len(opus_data)}")

        decoded_data = opus_decoder.decode(bytearray(opus_data))  # type: ignore
        if decoded_data is not None:
            decoded_data = np.frombuffer(decoded_data, dtype=np.int16)
            assert len(decoded_data) == CHUNK
            # logger.debug(f"Decoded audio of length: {len(decoded_data)}")
        else:
            logger.error("Error in audio decoding. decoded_data is None")
        return decoded_data
    except Exception as e:
        logger.error(f"Error in audio decoding: {e}")
        return None


async def async_sender(connection, response_queue: Queue):
    logger.info("Client connected.")
    try:
        while True:
            response = response_queue.get()
            logger.debug(f"Sending response: {response}")
            await connection.send(response)
    except websockets.exceptions.ConnectionClosed as e:
        logger.debug(f"Client disconnected with exception: {e}")
    except asyncio.CancelledError as e:
        logger.debug("Receive Socket operation cancelled")
    except Exception as e:
        logger.error(f"Error in receive socket: {e}")
