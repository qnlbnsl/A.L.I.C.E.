import asyncio
from multiprocessing import Queue
from multiprocessing.synchronize import Event
from typing import Self, cast
from websockets.legacy.server import WebSocketServerProtocol
import websockets
import base64
import json
from pyogg import OpusEncoder, OpusDecoder  # type: ignore
import numpy as np

from numpy.typing import NDArray

from logger import logger

from enums import CHUNK, RATE


class OpusDecoderManager:
    def __init__(self: Self, sample_rate: int, channels: int = 1) -> None:
        self.decoder = OpusDecoder()
        self.decoder.set_sampling_frequency(sample_rate)  # type: ignore
        self.decoder.set_channels(channels)  # type: ignore

    def decode_audio(
        self,
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
                audio = np.frombuffer(cast(bytes, decoded_data), dtype=np.int16)
                assert len(audio) == CHUNK
                return audio
                # logger.debug(f"Decoded audio of length: {len(decoded_data)}")
            else:
                logger.error("Error in audio decoding. decoded_data is None")
            return None
        except Exception as e:
            logger.error(f"Error in audio decoding: {e}")
            return None


async def async_receiver(
    connection: WebSocketServerProtocol,
    decoded_audio_queue: "Queue[NDArray[np.float32]]",
    question_event: Event,
    wake_word_event: Event,
) -> None:
    decoder = OpusDecoderManager(RATE, 1)
    logger.info("Client connected.")
    try:
        while True:
            message = await connection.recv()
            # logger.debug(f"Received: {message}")
            data = json.loads(message)
            if data["type"] == "audio":
                # Decode the base64 message
                decoded_audio_int16 = decoder.decode_audio(data["data"])
                if decoded_audio_int16 is None:
                    logger.error("Error in audio decoding. decoded_audio is None")
                    continue
                decoded_audio: NDArray[np.float32] = (
                    decoded_audio_int16.astype(np.float32) / 32768.0
                )
                decoded_audio_queue.put(decoded_audio)
                # decoded_audio.astype(np.float32, order="C") / 32768.0
                # Write the decoded bytes to the WAV file
            elif data["type"] == "config":
                logger.debug(f"Received config: {data}")
                sample_rate = data["sample_rate"]
                channels = data["channels"]
                # reinitialize the decoder with the new sample rate and channels
                decoder = OpusDecoderManager(sample_rate=sample_rate, channels=channels)
            elif data["type"] == "interrupt":
                logger.debug(f"Received interrupt: {data}")
                # Bypass the wake word and start actively parsing the question
                # Allows for the user to interrupt the assistant.
                question_event.set()
            elif data["type"] == "wake_word":
                logger.debug(f"Received wake_word: {data}")
                # Allow client to set wake word
                # Allows for a traditional approach to wake word detection for streaming.
                wake_word_event.set()
            else:
                logger.debug(f"Received unknown message: {data}")
    except websockets.exceptions.ConnectionClosed as e:
        logger.debug(f"Client disconnected with exception: {e}")
    except asyncio.CancelledError as e:
        logger.debug("Receive Socket operation cancelled")
    except Exception as e:
        logger.error(f"Error in receive socket: {e}")
