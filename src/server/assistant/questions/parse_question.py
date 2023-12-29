from multiprocessing import Queue
from multiprocessing.synchronize import Event
import time

from logger import logger


def parse_question(shutdown_event: Event, question_queue: Queue, wake_word_event: Event):
    while shutdown_event.is_set() is False and wake_word_event.is_set() is True:
        question = question_queue.get()
        if question is None:
            time.sleep(1)
            continue
        logger.debug(question)
        # question_queue.task_done()
    wake_word_event.clear()
