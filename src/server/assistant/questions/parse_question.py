from multiprocessing import Queue
from multiprocessing.synchronize import Event

from logger import logger


def parse_question(shutdown_event: Event, question_queue: Queue[str], wake_word_event: Event, response_event: Event) -> str | None:
    while shutdown_event.is_set() is False:
        question = question_queue.get()
        logger.debug(question)
        answer = answer_question(question)
        wake_word_event.clear()
        response_event.set()
        return answer
        # question_queue.task_done()
    return None

def answer_question(question: str) -> str:
    return "I don't know"