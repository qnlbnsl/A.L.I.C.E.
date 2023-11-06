import asyncio
import argparse
import base64
import numpy as np

from pathlib import Path
from threading import Thread
from typing import Text, Optional

import rx.operators as ops
import websockets

from . import argdoc
from . import sources as src

def encode_audio(waveform: np.ndarray) -> Text:
    data = waveform.astype(np.float32).tobytes()
    return base64.b64encode(data).decode("utf-8")


def decode_audio(data: Text) -> np.ndarray:
    # Decode chunk encoded in base64
    byte_samples = base64.decodebytes(data.encode("utf-8"))
    # Recover array from bytes
    samples = np.frombuffer(byte_samples, dtype=np.float32)
    return samples.reshape(1, -1)


async def encode_and_send(ws, audio_chunk):
    encoded_audio = encode_audio(audio_chunk)
    await ws.send(encoded_audio)

async def send_audio(ws: websockets.WebSocketClientProtocol, source: Text, step: float, sample_rate: int):
    # Create audio source
    source_components = source.split(":")
    device = int(source_components[1]) if len(source_components) > 1 else None
    audio_source = src.MicrophoneAudioSource(step, device)

    # Start reading audio and send it through the websocket
    await audio_source.stream.pipe(
        ops.map(encode_audio),
        ops.flat_map(lambda audio_chunk: encode_and_send(ws, audio_chunk))
    ).run()



async def receive_audio(ws: websockets.WebSocketClientProtocol, output: Optional[Path]):
    while True:
        message = await ws.recv()
        print(f"Received: {message}", end="")
        if output is not None:
            with open(output, "a") as file:
                file.write(message)


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
        "--step", default=0.5, type=float, help=f"{argdoc.STEP}. Defaults to 0.5"
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

    # Run websocket client
    
    async with websockets.connect(f"ws://{args.host}:{args.port}") as ws:
        sender = Thread(
            target=send_audio, args=[ws, args.source, args.step, args.sample_rate]
        )
        receiver = Thread(target=receive_audio, args=[ws, args.output_file])
        sender.start()
        receiver.start()


if __name__ == "__main__":
    asyncio.run(run())
    # run()