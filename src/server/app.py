import asyncio
import time

from multiprocessing import Process, Queue, Manager, Event
import torch.multiprocessing as mp

from stt.stt import transcribe

import websockets as ws
from websockets.legacy.server import Serve

from ws_server.receiver import async_receiver
from ws_server.sender import async_sender


from assistant.process import process_segments
from assistant.concept_store.parse_concept import parse_concept
from assistant.intents.parse_intent import parse_intent
from assistant.questions.parse_question import parse_question

from logger import logger

# Set the start method for multiprocessing
mp.set_start_method("spawn", force=True)
# set_start_method("spawn", force=True)


def start_async_server(
    manager_queue,
    response_queue,
    stt_ready_event,
    process_segments_ready_event,
    host="0.0.0.0",
    port=8765,
) -> Serve:
    async def handler(websocket, path):
        await async_receiver(websocket, manager_queue)
        await async_sender(websocket, response_queue)

    is_ready = False
    time_taken = 0
    logger.debug("Waiting for STT and Process Segments to be ready")
    while not is_ready:
        if stt_ready_event.is_set() and process_segments_ready_event.is_set():
            is_ready = True
        else:
            time.sleep(1)  # Sleep for 1 second
            time_taken += 1
    logger.info(f"STT and Process Segments are ready after {time_taken} seconds")
    return ws.serve(handler, host, port)


def create_processes(
    shutdown_event,
    decoded_audio_queue,
    transcribed_text_queue,
    concept_queue,
    stt_ready_event,
    question_queue,
    intent_queue,
    response_queue,
    process_segments_ready_event,
):
    processes = []
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
    intent_process = Process(target=parse_intent, args=(shutdown_event, intent_queue))
    question_process = Process(
        target=parse_question, args=(shutdown_event, question_queue)
    )
    processes.append(concept_process)
    processes.append(intent_process)
    processes.append(question_process)
    return processes


def main():
    logger.info("Starting server")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    manager = Manager()
    # Communication Queues
    decoded_audio_queue = manager.Queue()  # Queue([NDArray[np.float32]])
    response_queue = manager.Queue()  # Queue([str])
    # IPC Queues
    transcribed_text_queue = Queue()  # Queue([str])
    concept_queue = Queue()  # Queue([segment])
    question_queue = Queue()  # Queue([str])
    intent_queue = Queue()  # Queue([str])

    # Create a shared event to signal shutdown
    shutdown_event = Event()
    # Create event to signal that Neural Networks are ready
    stt_ready_event = Event()
    process_segments_ready_event = Event()
    # Skip Processing Events
    music_event = Event()
    stop_listening_event = Event()
    wake_word_mode_event = Event()

    processes = create_processes(
        shutdown_event,
        decoded_audio_queue,
        transcribed_text_queue,
        concept_queue,
        stt_ready_event,
        question_queue,
        intent_queue,
        response_queue,
        process_segments_ready_event,
    )
    try:
        logger.info("Starting processes")
        for process in processes:
            process.start()

    except Exception as e:
        logger.error(f"Error in creating processes: {e}")
        raise e

    try:
        server = start_async_server(
            decoded_audio_queue,
            stt_ready_event,
            response_queue,
            process_segments_ready_event,
        )
        loop.run_until_complete(server)
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
