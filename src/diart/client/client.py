import asyncio
import argparse
import base64
import numpy as np

from pathlib import Path
from threading import Thread
from typing import Text, Optional

import rx.operators as ops
import websockets

import argdoc
import sources as src

def encode_audio(waveform: np.ndarray) -> Text:
    try:
        data = waveform.astype(np.float32).tobytes()
        return base64.b64encode(data).decode("utf-8")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

def decode_audio(data: Text) -> np.ndarray:
    # Decode chunk encoded in base64
    byte_samples = base64.decodebytes(data.encode("utf-8"))
    # Recover array from bytes
    samples = np.frombuffer(byte_samples, dtype=np.float32)
    return samples.reshape(1, -1)


async def encode_and_send(ws, audio_chunk):
    # print("encoding")
    encoded_audio = encode_audio(audio_chunk)
    # print("sending")
    await ws.send(encoded_audio)
    # print("sent")

async def send_audio(ws: websockets.WebSocketClientProtocol, source: Text, step: float, sample_rate: int):
    # Create audio source
    print("starting send audio")
    source_components = source.split(":")
    device = int(source_components[1],10) if len(source_components) > 1 else None
    loop = asyncio.get_running_loop()
    audio_source = src.MicrophoneAudioSource(step, device=device, loop=loop)

    try:
        print("Starting the audio stream")
        # Start the audio stream
        audio_source.start()

        async for audio_chunk in audio_source:
            await encode_and_send(ws, audio_chunk)

    except Exception as e:
        print(f"exception: {e}")


async def receive_audio(ws: websockets.WebSocketClientProtocol, output: Optional[Path]):
    try:
        while True:
            message = await ws.recv()
            print(f"Received: {message}", end="")
            if output is not None:
                with open(output, "a") as file:
                    file.write(message)
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"WebSocket connection closed: {e}")

async def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True, type=str, help="Server host")
    parser.add_argument("--port", required=True, type=int, help="Server port")
    parser.add_argument(
        "source",
        type=str,
        help="Path to an audio file | 'microphone' | 'microphone:<DEVICE_ID>'",
        default=2
    )
    parser.add_argument(
        "--step", default=20, type=float, help=f"{argdoc.STEP}. Defaults to 20"
    )
    parser.add_argument(
        "-sr",
        "--sample-rate",
        default=44100,
        type=int,
        help=f"{argdoc.SAMPLE_RATE}. Defaults to 16000",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        type=Path,
        help="Output RTTM file. Defaults to no writing",
    )
    args = parser.parse_args()

    async with websockets.connect(f"ws://{args.host}:{args.port}") as ws:
        print("socket connected")
        
        step = 0.02 # args.step // 1000
        
        send_task = asyncio.create_task(send_audio(ws, args.source, step, args.sample_rate))
        receive_task = asyncio.create_task(receive_audio(ws, args.output_file))
        try:
            await asyncio.gather(send_task, receive_task)
        except KeyboardInterrupt:
            exit(0)
if __name__ == "__main__":
    asyncio.run(run())
    # run()