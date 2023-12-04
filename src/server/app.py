import asyncio

from multiprocessing import Process, set_start_method, Queue, Manager, Event
import time

# from multiprocessing.synchronize import Event
from numpy.typing import NDArray
import numpy as np

import torch.multiprocessing as mp

from websockets.sync.server import serve
import websockets as ws

from logger import logger
from receiver import async_receiver
from stt.stt import transcribe

from assistant.process import process_segments
from assistant.concept_store.parse_concept import parse_concept
from assistant.intents.parse_intent import parse_intent
from assistant.questions.parse_question import parse_question

# Set the start method for multiprocessing
mp.set_start_method("spawn", force=True)
# set_start_method("spawn", force=True)


def start_async_server(
    manager_queue,
    stt_ready_event,
    process_segments_ready_event,
    host="0.0.0.0",
    port=8765,
):
    async def handler(websocket, path):
        await async_receiver(websocket, manager_queue)

    is_ready = False
    while not is_ready:
        if stt_ready_event.is_set() and process_segments_ready_event.is_set():
            is_ready = True
        else:
            logger.debug("Waiting for STT and Process Segments to be ready")
            time.sleep(1)  # Sleep for 1 second
    return ws.serve(handler, host, port)


def main():
    logger.info("Starting server")
    manager = Manager()
    decoded_audio_queue = manager.Queue()  # Queue([NDArray[np.float32]])
    transcribed_text_queue = Queue()  # Queue([str])
    concept_queue = Queue()  # Queue([segment])
    question_queue = Queue()  # Queue([str])
    intent_queue = Queue()  # Queue([str])

    # Create a shared event to signal shutdown
    shutdown_event = Event()
    # Create event to signal that Neural Networks are ready
    stt_ready_event = Event()
    process_segments_ready_event = Event()

    processes = []
    try:
        loop = asyncio.get_event_loop()
        server = start_async_server(
            decoded_audio_queue, stt_ready_event, process_segments_ready_event
        )
        loop.run_until_complete(server)

        stt_process = mp.Process(
            target=transcribe,
            args=(
                shutdown_event,
                decoded_audio_queue,
                transcribed_text_queue,
                concept_queue,
                stt_ready_event,
            ),
        )
        processes.append(stt_process)

        process_segments_process = mp.Process(
            target=process_segments,
            args=(
                shutdown_event,
                transcribed_text_queue,
                question_queue,
                intent_queue,
                process_segments_ready_event,
            ),
        )
        processes.append(process_segments_process)
        # these processes do not require a ready event.
        concept_process = Process(
            target=parse_concept, args=(shutdown_event, concept_queue)
        )
        intent_process = Process(
            target=parse_intent, args=(shutdown_event, intent_queue)
        )
        question_process = Process(
            target=parse_question, args=(shutdown_event, question_queue)
        )
        processes.append([concept_process, intent_process, question_process])
    except Exception as e:
        logger.error(f"Error in creating processes: {e}")
        raise e

    logger.info("Starting processes")
    for process in processes:
        process.start()

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Shutdown signal received")
        shutdown_event.set()
    finally:
        for process in processes:
            if process is not None and process.is_alive():
                process.terminate()
                process.join()
                logger.info(f"Process {process} joined")
        loop.close()


if __name__ == "__main__":
    main()
