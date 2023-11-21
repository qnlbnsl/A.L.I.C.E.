import asyncio
import base64
import numpy as np
from numpy.typing import NDArray


from pyogg import OpusEncoder, OpusDecoder  # type: ignore # Pylance issue

from pathlib import Path
from typing import Text, Optional

import websockets

import classes.sources as src

import wave
import json

from logger import logger
from enums import CHUNK, RATE

silent_waveform = np.zeros(CHUNK, dtype=np.int16)  # Using int16 for 16-bit audio
# Create an asyncio Event object
playback_event = asyncio.Event()

# Create an Opus encoder/decoder
opus_encoder = OpusEncoder()
opus_decoder = OpusDecoder()

opus_encoder.set_application("audio")

opus_encoder.set_sampling_frequency(RATE)
opus_decoder.set_sampling_frequency(RATE)

opus_encoder.set_channels(1)
opus_decoder.set_channels(1)


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


def is_silent_audio(audio_chunk: NDArray[np.int16]) -> bool:
    return np.array_equal(audio_chunk, silent_waveform)


# Function to check the flag
def is_replying() -> bool:
    return playback_event.is_set()


async def encode_and_send(
    ws: websockets.WebSocketClientProtocol, audio_chunk: NDArray[np.int16]
):
    if is_replying() or is_silent_audio(audio_chunk):
        return
    try:
        # logger.debug("encoding")
        encoded_audio = encode_audio(audio_chunk)
        # logger.debug("sending")
        await ws.send(json.dumps({"type": "audio", "data": encoded_audio}))
        # logger.debug("sent")
    except Exception as e:
        logger.error(f"Error in sending audio: {e}")
        exit(1)


async def send_audio(
    ws: websockets.WebSocketClientProtocol, source: Text, step: float, sample_rate: int
):
    # Create audio source
    logger.debug("Starting Audio Send Function")
    source_components = source.split(":")
    device = int(source_components[1], 10) if len(source_components) > 1 else None
    loop = asyncio.get_running_loop()
    audio_source = src.MicrophoneAudioSource(step, device=device, loop=loop)

    try:
        logger.debug("Starting the microphone source stream")
        # Start the audio stream
        audio_source.start()
        async for audio_chunk in audio_source:
            # print(".", end="", flush=True)
            await encode_and_send(ws, audio_chunk)
    except Exception as e:
        logger.error(f"exception: {e}")
    except asyncio.CancelledError as e:
        logger.debug("Send Socket operation cancelled")
    finally:
        logger.debug("Awaiting close audio source")
        await audio_source.close()


async def record_and_send_audio(
    ws: websockets.WebSocketClientProtocol, source: Text, step: float, sample_rate: int
):
    # Create audio source
    logger.debug("starting send audio")
    source_components = source.split(":")
    device = int(source_components[1], 10) if len(source_components) > 1 else None
    loop = asyncio.get_running_loop()
    audio_source = src.MicrophoneAudioSource(step, device=device, loop=loop)

    try:
        logger.debug("Starting the audio stream")
        # Start the audio stream
        audio_source.start()

        with wave.open("output.wav", "wb") as wav_file:
            wav_file.setnchannels(8)
            wav_file.setsampwidth(
                2
            )  # Assuming that audio chunks are float32 which is 4 bytes
            wav_file.setframerate(sample_rate)
            async for audio_chunk in audio_source:
                print(".", end="", flush=True)  # Progress indicator
                wav_file.writeframes(audio_chunk.tobytes())
                await encode_and_send(ws, audio_chunk)

    except Exception as e:
        logger.error(f"exception: {e}")
    except asyncio.CancelledError as e:
        logger.debug("Send Socket operation cancelled")
    finally:
        await audio_source.close()


async def receive_audio(ws: websockets.WebSocketClientProtocol, output: Optional[Path]):
    try:
        while True:
            message = await ws.recv()
            logger.debug(f"Received: {message}")
            if output is not None:
                with open(output, "a") as file:
                    file.write(message)
            # check for message type
            # if message type is start_playbacck
            # Set playback flag to true
            # if message type is stop_playback
            # Set playback flag to false
            # if message type is audio
            # check if playback flag is true
            # if true then decode and play audio
            # else ignore

    except websockets.exceptions.ConnectionClosedError as e:
        logger.debug(f"WebSocket connection closed: {e}")
    except asyncio.CancelledError as e:
        logger.debug("Recv Socket operation cancelled")
