# Desc: Main entry point for the server
import asyncio
from ws_server.server import start_async_server

import torch.multiprocessing as mp
from multiprocessing import Process, Manager, Event, get_context
from multiprocessing.synchronize import Event as Ev
from multiprocessing.queues import Queue

from speech_to_text.stt import stt
from faster_whisper.transcribe import Segment

from assistant.process import process_segments
from assistant.concept_store.parse_concept import parse_concept
from assistant.parse_commands.parse_command import parse_command
from assistant.parse_questions.parse_question import parse_question

from typing import Any, List
from logger import logger

# Set the start method for multiprocessing
mp.set_start_method(
    "spawn", force=True
)  # Required for pytorch to work with multiprocessing


def create_processes(
    shutdown_event: Ev,
    decoded_audio_queue: Any,  # Queue([NDArray[np.float32]])
    transcribed_text_queue: "Queue[str]",
    concept_queue: "Queue[Segment]",
    stt_ready_event: Ev,
    question_queue: "Queue[str]",
    intent_queue: "Queue[str]",
    response_queue: Any,  # Queue([str])
    wake_word_event: Ev,
    question_event: Ev,
    process_segments_ready_event: Ev,
    thinking_event: Ev,
) -> List[Process]:
    processes: List[Process] = []
    stt_process = mp.Process(
        name="stt",
        target=stt,
        args=(
            shutdown_event,
            decoded_audio_queue,
            transcribed_text_queue,
            concept_queue,
            stt_ready_event,
            wake_word_event,
        ),
    )
    processes.append(stt_process)

    process_segments_process = mp.Process(
        target=process_segments,
        name="process_segments",
        args=(
            shutdown_event,
            transcribed_text_queue,
            question_queue,
            intent_queue,
            process_segments_ready_event,
            question_event,
            5.0,  # timeout
        ),
    )
    processes.append(process_segments_process)
    # these processes do not require a ready event.
    concept_process = Process(
        target=parse_concept, name="parse_concept", args=(shutdown_event, concept_queue)
    )
    intent_process = Process(
        target=parse_command,
        name="parse_command",
        args=(
            shutdown_event,
            wake_word_event,
            thinking_event,
            intent_queue,
            response_queue,
        ),
    )
    question_process = Process(
        target=parse_question,
        name="parse_question",
        args=(
            shutdown_event,
            question_event,
            thinking_event,
            wake_word_event,
            question_queue,
            response_queue,
        ),
    )
    processes.append(concept_process)
    processes.append(intent_process)
    processes.append(question_process)
    return processes


def main() -> None:
    logger.info("Starting server")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    manager = Manager()
    # Communication Queues
    decoded_audio_queue = manager.Queue()  # Queue([NDArray[np.float32]])
    response_queue = manager.Queue()  # Queue([str])
    # IPC Queues
    ctx = get_context("spawn")
    transcribed_text_queue: "Queue[str]" = ctx.Queue()  # Queue([str])
    concept_queue: "Queue[Segment]" = ctx.Queue()  # Queue([segment])
    question_queue: "Queue[str]" = ctx.Queue()  # Queue([str])
    intent_queue: "Queue[str]" = ctx.Queue()  # Queue([str])

    # Create a shared event to signal shutdown
    shutdown_event = Event()
    # Create event to signal that Neural Networks are ready
    stt_ready_event = Event()
    process_segments_ready_event = Event()
    # Skip Processing Events
    _music_event = Event()
    _stop_listening_event = Event()
    wake_word_event = Event()
    question_event = Event()
    thinking_event = Event()

    processes = create_processes(
        shutdown_event=shutdown_event,
        decoded_audio_queue=decoded_audio_queue,
        transcribed_text_queue=transcribed_text_queue,
        concept_queue=concept_queue,
        stt_ready_event=stt_ready_event,
        question_queue=question_queue,
        intent_queue=intent_queue,
        response_queue=response_queue,
        wake_word_event=wake_word_event,
        process_segments_ready_event=process_segments_ready_event,
        question_event=question_event,
        thinking_event=thinking_event,
    )
    try:
        logger.info("Creating processes. Please wait...")
        for process in processes:
            logger.info(f"Starting process: {process.name}")
            process.start()

    except Exception as e:
        logger.error(f"Error in creating processes: {e}")
        raise e

    try:
        server = start_async_server(
            manager_queue=decoded_audio_queue,
            stt_ready_event=stt_ready_event,
            response_queue=response_queue,
            process_segments_ready_event=process_segments_ready_event,
            thinking_event=thinking_event,
            question_event=question_event,
            wake_word_event=wake_word_event,
        )
        loop.run_until_complete(server)
        loop.run_forever()
    except KeyboardInterrupt:
        print("Shutdown signal received")
        shutdown_event.set()
    finally:
        for process in processes:
            if process and process.is_alive():
                process.terminate()
                process.join()
                logger.info(f"Process {process} joined")
        loop.close()


if __name__ == "__main__":
    main()
