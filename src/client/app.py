import asyncio
import argparse
from pathlib import Path
import websockets

from audio import send_audio, receive_audio

from logger import logger

async def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True, type=str, help="Server host")
    parser.add_argument("--port", required=True, type=int, help="Server port")
    parser.add_argument(
        "source",
        type=str,
        help="Path to an audio file | 'microphone' | 'microphone:<DEVICE_ID>'",
        default="microphone:2",
    )
    parser.add_argument(
        "--step",
        default=20,
        type=float,
        help=f"Sliding window step (in milliseconds). Defaults to 20",
    )
    parser.add_argument(
        "-sr",
        "--sample-rate",
        default=44100,
        type=int,
        help=f"Sample rate of the audio stream. Defaults to 44100",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        type=Path,
        help="Output RTTM file. Defaults to no writing",
    )
    args = parser.parse_args()
    try:
        async with websockets.connect(f"ws://{args.host}:{args.port}") as ws:
            logger.debug("socket connected")

            step = 0.2  # args.step // 1000

            send_task = asyncio.create_task(
                send_audio(ws, args.source, step, args.sample_rate)
            )
            receive_task = asyncio.create_task(receive_audio(ws, args.output_file))
            await asyncio.gather(send_task, receive_task)
    except KeyboardInterrupt:
        logger.debug("Interrupt received, shutting down.")
    except asyncio.CancelledError as e:
        logger.debug(f"ALL Operations cancelled: {e}")
    finally:
        # Close the event loop
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        list(map(lambda task: task.cancel(), tasks))
        await asyncio.gather(*tasks, return_exceptions=True)
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.stop()
        logger.debug("Cleanup complete.")


if __name__ == "__main__":
    asyncio.run(run())
