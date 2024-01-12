import asyncio
from multiprocessing import Queue
from multiprocessing.synchronize import Event
from websockets.legacy.server import WebSocketServerProtocol
import websockets

# from pyogg import OpusEncoder, OpusDecoder  # type: ignore
import numpy as np

from numpy.typing import NDArray

# from typing import cast

from logger import logger


async def async_sender(
    connection: WebSocketServerProtocol,
    response_queue: "Queue[NDArray[np.float32]]",
) -> None:
    logger.info("Client connected.")
    try:
        while True:
            response = response_queue.get()
            logger.debug(f"Sending response: {response}")
            await connection.send({"thinking": False})
            await connection.send(response)
    except websockets.exceptions.ConnectionClosed as e:
        logger.debug(f"Client disconnected with exception: {e}")
    except asyncio.CancelledError as e:
        logger.debug("Receive Socket operation cancelled")
    except Exception as e:
        logger.error(f"Error in receive socket: {e}")


async def async_thinking(
    connection: WebSocketServerProtocol, thinking_event: Event
) -> None:
    logger.info("Client connected.")
    try:
        while True:
            thinking_event.wait()
            logger.debug(f"Activating thinking mode")
            await connection.send({"thinking": True})
    except websockets.exceptions.ConnectionClosed as e:
        logger.debug(f"Client disconnected with exception: {e}")
    except asyncio.CancelledError as e:
        logger.debug("Receive Socket operation cancelled")
    except Exception as e:
        logger.error(f"Error in receive socket: {e}")
