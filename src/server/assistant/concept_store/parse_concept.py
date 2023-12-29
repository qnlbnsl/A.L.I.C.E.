from multiprocessing import Queue
from multiprocessing.synchronize import Event
import time
from faster_whisper.transcribe import Segment
from logger import logger


def parse_concept(shutdown_event: Event, concept_queue: Queue[Segment]) -> None:
    while shutdown_event.is_set() is False:
        concept = concept_queue.get()
        logger.debug(f"Received concept: {concept.text}")
        # concept_queue.task_done()


def add_to_db(segment: Segment) -> None:
    logger.debug(f"Adding segment to DB: {segment.text}")