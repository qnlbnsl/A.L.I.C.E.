import asyncio
import time

from logger import logger

concept_queue = asyncio.Queue()


async def parse_concept():
    while True:
        concept = await concept_queue.get()
        if concept is None:
            # sleep for a second to avoid busy waiting
            time.sleep(1)
            continue
        logger.debug(f"Received concept: {concept.text}")
        # concept_queue.task_done()
