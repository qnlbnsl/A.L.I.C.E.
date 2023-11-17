import asyncio
import time

from logger import logger

question_queue = asyncio.Queue()


async def parse_question():
    while True:
        question = await question_queue.get()
        if question is None:
            time.sleep(1)
            continue
        logger.debug(question)
        # question_queue.task_done()
