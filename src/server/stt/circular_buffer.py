import asyncio
import numpy as np
import time
from logger import logger

dtype = np.float32


class CircularBuffer:
    def __init__(self, capacity, sample_rate):
        # Buffer size based on capacity in seconds and sample rate
        self.buffer = np.zeros(capacity * sample_rate, dtype=dtype)
        self.capacity = capacity
        self.sample_rate = sample_rate
        self.write_pos = 0
        self.read_pos = 0
        self.lock = asyncio.Lock()
        self.data_added_event = asyncio.Event()
        self.last_write_time = 0  # initialize to 0

    async def write(self, data):
        async with self.lock:
            data = data.astype(dtype)
            self.last_write_time = time.time()
            self.data_added_event.set()  # Set the event to indicate data has been added
            available_space = len(self.buffer) - self.write_pos
            # logger.debug(f"Available space in buffer: {available_space}")
            if len(data) > available_space:
                # If we have more data than space, wrap around the buffer
                # logger.debug("Wrapping around buffer and overwriting old data")
                self.buffer[self.write_pos :] = data[:available_space]
                self.buffer[: len(data) - available_space] = data[available_space:]
                self.write_pos = len(data) - available_space
            else:
                # If we have enough space, just write the data
                self.buffer[self.write_pos : self.write_pos + len(data)] = data
                self.write_pos += len(data)

            # If we've reached the end of the buffer, wrap the position
            if self.write_pos >= len(self.buffer):
                # logger.debug("Wrapping around buffer")
                self.write_pos = 0

    async def read(self, duration):
        async with self.lock:
            data_size = int(duration * self.sample_rate)
            read_pos = self.write_pos - data_size

            if read_pos < 0:
                read_pos += len(self.buffer)
                data = np.concatenate(
                    (self.buffer[read_pos:], self.buffer[: self.write_pos])
                )
            else:
                data = self.buffer[read_pos : self.write_pos]

            # Update read_pos to the end of the read data
            self.read_pos = self.write_pos

            return data

    def get_buffer_duration(self):
        """Calculate the current duration of audio data in the buffer."""
        if self.write_pos >= self.read_pos:
            samples_in_buffer = self.write_pos - self.read_pos
        else:
            samples_in_buffer = len(self.buffer) - self.read_pos + self.write_pos
        return samples_in_buffer / self.sample_rate

    async def data_added(self):
        while True:
            await self.data_added_event.wait()  # Wait for data to be added

            # Continuously check if 5 seconds have passed since the last data write
            while True:
                if time.time() - self.last_write_time > 5:
                    # Clear the flag if more than 5 seconds have passed since the last write
                    self.data_added_event.clear()
                    return True
                await asyncio.sleep(0.1)  # Sleep to prevent a busy wait
