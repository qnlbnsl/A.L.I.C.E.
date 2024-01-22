from multiprocessing import Queue
from multiprocessing.synchronize import Event
from time import sleep

from logger import logger


def parse_question(
    shutdown_event: Event,
    question_event: Event,
    thinking_event: Event,
    wake_word_event: Event,
    question_queue: "Queue[str]",
    response_queue: "Queue[str]",
) -> None:
    logger.info("Parse Question Ready")
    while shutdown_event.is_set() is False:
        question = question_queue.get()
        thinking_event.set()
        logger.debug(question)
        answer = answer_question(question)  # Blocking operation
        response_queue.put(answer)
        question_event.clear()
        thinking_event.clear()
        wake_word_event.clear()
        # question_queue.task_done()


def answer_question(question: str) -> str:
    sleep(30)
    return "I don't know"
