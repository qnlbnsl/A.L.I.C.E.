import time
from multiprocessing import Lock, Queue
from threading import Thread
from multiprocessing.synchronize import Event
from typing import List, Self

from logger import logger

class QuestionBuffer:
    def __init__(self: Self, question_queue: Queue[str], max_question_length: int = 10,timeout: float = 5.0)-> None:
        self._lock = Lock()
        # initialize empty buffers
        self._buffer: List[str] = []
        self._question_len = 0
        self._last_update_time = time.time()
        # Assign defaults
        self.max_question_length = max_question_length
        self.timeout = timeout # seconds before question is considered complete.
        # Assign queue object
        self.queue = question_queue
        # Create thread to check for timeout
        self._stop_thread = False
        self.thread: Thread = Thread()

    
    # Add sentence to buffer
    def _add_sentence(self: Self, sentence: str)-> None:
        with self._lock:
            self._buffer.append(sentence.strip())
            self._last_update_time = time.time()
            # Check if thread is running and start it if not.
            if self.thread.is_alive() is False:
                # Python requires that a thread be recreated after it has been stopped.
                self.thread = Thread(target=self._check_and_execute_timeout, daemon=True)
                self.thread.start()
            if len(self._buffer) > self.max_question_length:
                self._execute_question()

    def _execute_question(self: Self)-> None:
        with self._lock:
            self._stop_thread = False
            if self.thread.is_alive():
                self.thread.join()
            question = " ".join(self._buffer)
            logger.debug(f"Question: {question}")
            self.queue.put(question)
            self._reset()
    # Reset buffer
    def _reset(self: Self)-> None:
        self._buffer = []
        self._question_len = 0

    # Only clear buffer
    def _clear_buffer(self: Self)-> None:
        self._buffer = []

    # Only reset question length
    def _clear_question(self: Self)-> None:
        self._question_len = 0

    def _check_timeout(self: Self) -> bool:
        with self._lock:
            if time.time() - self._last_update_time > self.timeout:
                return True
        return False
    
    def _check_and_execute_timeout(self: Self) -> None:
        while not self._stop_thread:
            time.sleep(1)  # Check every 1 second
            if self._check_timeout():
                self._execute_question()
    
    # handle question based on whether it is a new question or a continuation of the previous one.
    def handle_question(
        self: Self,
        sentence: str,
        question_event: Event,
    ) -> None:
        if question_event.is_set(): # Question is in progress. Flag cleared by the question process.
            self._add_sentence(sentence)
        else:
            question_event.set()
            self._reset()
            self._buffer.append(sentence)

    def _stop(self: Self) -> None:
        self._stop_thread = True
        self.thread.join()