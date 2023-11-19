import asyncio
import base64
import numpy as np

from pathlib import Path
from typing import Text, Optional

import websockets

import sources as src
import wave
import json

from beamforming import beamform_audio
from logger import logger


def encode_audio(waveform: np.ndarray) -> Text:
    try:
        data = waveform.astype(np.int16).tobytes()
        return base64.b64encode(data).decode("utf-8")
    except Exception as e:
        logger.error(f"Error: {e}")
        exit(1)


def decode_audio(data: Text) -> np.ndarray:
    # Decode chunk encoded in base64
    byte_samples = base64.decodebytes(data.encode("utf-8"))
    # Recover array from bytes
    samples = np.frombuffer(byte_samples, dtype=np.int16)
    return samples.reshape(1, -1)


async def encode_and_send(ws: websockets.WebSocketClientProtocol, audio_chunk):
    # logger.debug("encoding")
    encoded_audio = encode_audio(audio_chunk)
    # logger.debug("sending")
    await ws.send(json.dumps({"type": "audio", "data": encoded_audio}))
    # logger.debug("sent")


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
    except websockets.exceptions.ConnectionClosedError as e:
        logger.debug(f"WebSocket connection closed: {e}")
    except asyncio.CancelledError as e:
        logger.debug("Recv Socket operation cancelled")
