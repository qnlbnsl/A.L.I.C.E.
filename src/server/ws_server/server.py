from multiprocessing.synchronize import Event

from typing import Any

import websockets as ws
from websockets.legacy.server import Serve, WebSocketServerProtocol

from ws_server.receiver import async_receiver
from ws_server.sender import async_sender, async_thinking

from logger import logger
import time


def start_async_server(
    manager_queue: Any,
    response_queue: Any,
    stt_ready_event: Event,
    process_segments_ready_event: Event,
    thinking_event: Event,
    question_event: Event,
    wake_word_event: Event,
    host: str = "0.0.0.0",
    port: int = 8765,
) -> Serve:
    async def handler(websocket: WebSocketServerProtocol, _path: str) -> None:
        await async_receiver(websocket, manager_queue, question_event, wake_word_event)
        await async_sender(websocket, response_queue)
        await async_thinking(websocket, thinking_event)

    is_ready = False
    time_taken = 0
    logger.info("Waiting for STT and Process Segments to be ready")
    while not is_ready:
        if stt_ready_event.is_set() and process_segments_ready_event.is_set():
            is_ready = True
        else:
            time.sleep(1)  # Sleep for 1 second
            time_taken += 1
    logger.info(f"STT and Process Segments are ready after {time_taken} seconds")
    return ws.serve(handler, host, port)
