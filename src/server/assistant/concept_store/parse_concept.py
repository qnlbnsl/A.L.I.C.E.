from multiprocessing import Queue
from multiprocessing.synchronize import Event
import time

from logger import logger


def parse_concept(shutdown_event: Event, concept_queue: Queue):
    while shutdown_event.is_set() is False:
        concept = concept_queue.get()
        if concept is None:
            # sleep for a second to avoid busy waiting
            time.sleep(1)
            continue
        logger.debug(f"Received concept: {concept.text}")
        # concept_queue.task_done()
