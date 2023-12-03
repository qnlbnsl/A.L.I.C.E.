from multiprocessing import Queue
from multiprocessing.synchronize import Event
import time
from logger import logger


# HASSIO Bindings.


def parse_intent(shutdown_event: Event, intent_queue: Queue):
    while shutdown_event.is_set() is False:
        intent = intent_queue.get()
        if intent is None:
            time.sleep(1)
            continue
        logger.debug(intent)
        # intent_queue.task_done()
