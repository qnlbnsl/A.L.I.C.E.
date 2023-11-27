import asyncio
import base64
import json
from line_profiler import profile
import numpy as np
from numpy.typing import NDArray
import pyaudio as pa
from pathlib import Path
from typing import List, Text, Optional
import websockets
import classes.sources as src
from encoder import encode_audio, decode_audio
import wave
from beamforming import beamform_audio
from client.logger import logger
from enums import CHUNK
from concurrent.futures import ProcessPoolExecutor

executor = ProcessPoolExecutor(max_workers=1)
silent_waveform = np.zeros(CHUNK, dtype=np.int16)  # Using int16 for 16-bit audio
# Create an asyncio Event object
playback_event = asyncio.Event()
audio_handler = pa.PyAudio()
beamformed_audio_queue = asyncio.Queue()


def is_silent_audio(audio_chunk: NDArray[np.int16]) -> bool:
    return np.array_equal(audio_chunk, silent_waveform)


# Function to check the flag
def is_replying() -> bool:
    return playback_event.is_set()


async def send_encoded_audio(ws: websockets.WebSocketClientProtocol):
    encode_audio = await beamformed_audio_queue.get()
    await ws.send(json.dumps({"type": "audio", "data": encode_audio}))


@profile
async def encode_task(
    audio_source: src.MicrophoneAudioSource, ws: websockets.WebSocketClientProtocol
):
    try:
        async for audio_chunk in audio_source:
            audio_array = np.frombuffer(audio_chunk, dtype=np.int16)
            # smaller_chunks = divide_audio_into_chunks(audio_array)

            data = beamform_audio(audio_array)
            logger.debug(f"Sending {len(data)} bytes")
            # Offload encoding to a separate process
            loop = asyncio.get_running_loop()
            encoded_audio = await loop.run_in_executor(executor, encode_audio, data)
            if encoded_audio is not None:
                await ws.send(json.dumps({"type": "audio", "data": encoded_audio}))
    except Exception as e:
        logger.error(f"Error in encode_task: {e}")
        exit(1)


@profile
def encode_task_2(audio_chunk, frames, time, status):
    try:
        audio_array = np.frombuffer(audio_chunk, dtype=np.int16)
        # smaller_chunks = divide_audio_into_chunks(audio_array)

        data = beamform_audio(audio_array)
        encoded_audio = encode_audio(data)

        beamformed_audio_queue.put_nowait(encoded_audio)
        # asyncio.run_coroutine_threadsafe(
        #     beamformed_audio_queue.put(encoded_audio), asyncio.get_event_loop()
        # )
    except Exception as e:
        logger.error(f"Error in encode_task: {e}")
        exit(1)
    return (None, pa.paContinue)


async def send_audio(
    ws: websockets.WebSocketClientProtocol, source: Text, step: float, sample_rate: int
):
    # Create audio source
    logger.debug("Starting Audio Send Function")
    source_components = source.split(":")
    device = int(source_components[1], 10) if len(source_components) > 1 else None
    loop = asyncio.get_running_loop()
    audio_source = src.MicrophoneAudioSource(step, device=device, loop=loop)
    astask = None
    try:
        logger.debug("Starting the microphone source stream")
        # Start the audio stream
        audio_source.start()
        # print(".", end="", flush=True)
        await encode_task(audio_source, ws)

    except Exception as e:
        logger.error(f"exception: {e}")
    except asyncio.CancelledError as e:
        logger.debug("Send Socket operation cancelled")
    finally:
        logger.debug("Awaiting close audio source")
        await audio_source.close()
        if astask is not None:
            await asyncio.gather(astask)


async def send_audio_2(
    ws: websockets.WebSocketClientProtocol, source: Text, step: float, sample_rate: int
):
    # Create audio source
    logger.debug("Starting Audio Send Function")
    source_components = source.split(":")
    device = int(source_components[1], 10) if len(source_components) > 1 else None
    loop = asyncio.get_running_loop()
    audio_source = audio_handler.open(
        format=pa.paInt16,
        channels=8,
        rate=sample_rate,
        input=True,
        frames_per_buffer=640,
        stream_callback=encode_task_2,
        input_device_index=device if isinstance(device, int) else None,
    )
    astask = None
    try:
        logger.debug("Starting the microphone source stream")
        # Start the audio stream
        audio_source.start_stream()
        # print(".", end="", flush=True)
        while True:
            await asyncio.sleep(0.1)

    except Exception as e:
        logger.error(f"exception: {e}")
    except asyncio.CancelledError as e:
        logger.debug("Send Socket operation cancelled")
    finally:
        logger.debug("Awaiting close audio source")
        audio_source.stop_stream()
        audio_handler.terminate()
        if astask is not None:
            await asyncio.gather(astask)


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
                await encode_task(ws, audio_chunk)

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
