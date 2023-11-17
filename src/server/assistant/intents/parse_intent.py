import asyncio
import time
from logger import logger

intent_queue = asyncio.Queue()
# HASSIO Bindings.


async def parse_intent():
    while True:
        intent = await intent_queue.get()
        if intent is None:
            time.sleep(1)
            continue
        logger.debug(intent)
        # intent_queue.task_done()
