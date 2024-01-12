from typing import Self
import numpy as np
from numpy.typing import NDArray
import time
# from logger import logger
from multiprocessing import Lock


class CircularBuffer:
    def __init__(self: Self, capacity: int, sample_rate: int) -> None:
        self.buffer = np.zeros(capacity * sample_rate, dtype=np.float32)
        self.capacity = capacity
        self.sample_rate = sample_rate
        self.write_pos = 0
        self.read_pos = 0
        self.lock = Lock()  # Replace asyncio.Lock with multiprocessing.Lock
        self.last_write_time: float = 0.0

    def write(self: Self, data: NDArray[np.float32]) -> None:
        with self.lock:  # Use the lock in a context manager
            self.last_write_time = time.time()
            available_space = len(self.buffer) - self.write_pos

            if len(data) > available_space:
                self.buffer[self.write_pos :] = data[:available_space]
                self.buffer[: len(data) - available_space] = data[available_space:]
                self.write_pos = len(data) - available_space
            else:
                self.buffer[self.write_pos : self.write_pos + len(data)] = data
                self.write_pos += len(data)

            if self.write_pos >= len(self.buffer):
                self.write_pos = 0

    def read(self: Self, duration: float) -> NDArray[np.float32]:
        with self.lock:  # Ensure thread safety during read
            data_size = int(duration * self.sample_rate)
            read_pos = self.write_pos - data_size
            data: NDArray[np.float32] = np.zeros(data_size, dtype=np.float32) # Initialize data to 0
            if read_pos < 0:
                read_pos += len(self.buffer)
                data = np.concatenate(
                    (self.buffer[read_pos:], self.buffer[: self.write_pos])
                )
            else:
                data = self.buffer[read_pos : self.write_pos]
            self.read_pos = self.write_pos
        return data

    def get_buffer_duration(self: Self) -> float:
        with self.lock:  # Ensure thread safety when calculating buffer duration
            if self.write_pos >= self.read_pos:
                samples_in_buffer = self.write_pos - self.read_pos
            else:
                samples_in_buffer = len(self.buffer) - self.read_pos + self.write_pos
            return samples_in_buffer / self.sample_rate
