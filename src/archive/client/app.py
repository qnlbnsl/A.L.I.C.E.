import asyncio
import argparse
import websockets
import time

from pathlib import Path


from client.logger import logger
from audio import send_audio_2, receive_audio

# from utils import plot_mic_strengths
from enums import RATE, BLOCK_DURATION


async def run_client(host, port, source, step, sample_rate, output_file):
    async with websockets.connect(f"ws://{host}:{port}") as ws:
        logger.debug("Socket connected")
        ms_step = step / 1000
        send_task = asyncio.create_task(
            send_audio_2(
                ws, source, ms_step, sample_rate
            )  # type:ignore # Pylance issue?
        )  # type:ignore # Pylance issue?
        receive_task = asyncio.create_task(receive_audio(ws, output_file))
        await asyncio.gather(send_task, receive_task)


async def run():
    args = get_args()
    retry_count = 0
    try:
        while retry_count < args.max_retries:
            try:
                await run_client(
                    args.host,
                    args.port,
                    args.source,
                    BLOCK_DURATION,
                    RATE,
                    args.output_file,
                )
                break  # If run_client completes without exceptions, exit loop
            # Exceptions
            except websockets.exceptions.ConnectionClosed:
                logger.debug("Connection closed, attempting to reconnect...")
            except OSError as e:
                logger.debug(f"OS error: {e}, attempting to reconnect...")
            except KeyboardInterrupt:
                logger.debug("Interrupt received, shutting down.")
                break
            except Exception as e:
                logger.debug(f"Unexpected exception: {e}")

            try:
                retry_count += 1
                if retry_count < args.max_retries:
                    logger.debug(
                        f"Waiting {args.retry_delay} seconds before retrying..."
                    )
                    time.sleep(args.retry_delay)  # Delay before retrying
                else:
                    logger.debug("Maximum retry attempts reached. Shutting down.")
            except KeyboardInterrupt:
                logger.debug("Exiting...")

    except asyncio.CancelledError:
        logger.debug("Task cancelled")
    # finally:
    #     if STATS_COLLECTION:
    #         await plot_mic_strengths()
    #         await plot_led()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="192.168.3.46", type=str, help="Server host")
    parser.add_argument("--port", default="8080", type=int, help="Server port")
    parser.add_argument(
        "--source",
        type=str,
        help="Path to an audio file | 'microphone' | 'microphone:<DEVICE_ID>'",
        default="microphone:2",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        type=Path,
        help="Output RTTM file. Defaults to no writing",
    )
    parser.add_argument(
        "-mr",
        "--max-retries",
        type=int,
        default=10,
        help="Maximum number of retries before process will terminate. Defaults to 10",
    )
    parser.add_argument(
        "-rd",
        "--retry-delay",
        type=int,
        default=5,
        help="Delay between socket connection retries (seconds). Defaults to 5 seconds",
    )
    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(run())
