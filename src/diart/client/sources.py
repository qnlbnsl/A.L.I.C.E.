from abc import ABC, abstractmethod
from asyncio import Queue, Event, run_coroutine_threadsafe , get_running_loop, get_event_loop, AbstractEventLoop

from typing import Text, Optional, Union, Tuple

import numpy as np
import sounddevice as sd
from rx.subject.subject import Subject





class AudioSource(ABC):
    """Represents a source of audio that can start streaming via the `stream` property.

    Parameters
    ----------
    uri: Text
        Unique identifier of the audio source.
    sample_rate: int
        Sample rate of the audio source.
    """

    def __init__(self, uri: Text, sample_rate: int):
        self.uri = uri
        self.sample_rate = sample_rate
        self.stream = Subject()

    @property
    def duration(self) -> Optional[float]:
        """The duration of the stream if known. Defaults to None (unknown duration)."""
        return None

    @abstractmethod
    def read(self):
        """Start reading the source and yielding samples through the stream."""
        pass

    @abstractmethod
    def close(self):
        """Stop reading the source and close all open streams."""
        pass

class MicrophoneAudioSource(AudioSource):
    """Audio source tied to a local microphone.

    Parameters
    ----------
    block_duration: int
        Duration of each emitted chunk in seconds.
        Defaults to 0.5 seconds.
    device: int | str | (int, str) | None
        Device identifier compatible for the sounddevice stream.
        If None, use the default device.
        Defaults to None.
    """

    def __init__(
        self,
        block_duration: float, # Seconds
        loop: AbstractEventLoop,
        device: Optional[Union[int, Text, Tuple[int, Text]]] = None,
    ):
        self.loop = loop or get_event_loop()
        # Use the highest? supported sample rate
        sample_rates = [16000, 32000, 44100, 48000]
        best_sample_rate = None
        for sr in sample_rates:
            try:
                sd.check_input_settings(device=device, samplerate=sr)
            except Exception:
                print("exception")
                pass
            else:
                best_sample_rate = sr
                # break # this would break on the first hit....
        if best_sample_rate is None:
            best_sample_rate = sample_rates[2]
            
        print(f"Input Device: {device} with a sample rate of: {best_sample_rate}")
        super().__init__(f"input_device:{device}", best_sample_rate)
        
        # Determine block size in samples and create input stream
        self.block_size = int(np.rint(block_duration * self.sample_rate))
        print("Block Size: ", self.block_size)
        
        self._queue = Queue()
        
        print("Initializing Input Stream")
        self._mic_stream = sd.InputStream(
            channels=8,
            samplerate=self.sample_rate,
            latency='low',
            blocksize=self.block_size,
            callback=self._read_callback,
            device=device,
            dtype=np.int16,
        )

    def _read_callback(self, indata, frames, time, status):
        if status:
            print("Status:", status)
        run_coroutine_threadsafe(self._queue.put(indata.copy()), self.loop)


    async def read(self):
        self.start()
        while not self._mic_stream.stopped:
            try:
                data = await self._queue.get()
                if data is None:
                    # This is the signal that the stream has ended
                    break
                self.stream.on_next(data)
            except Exception as e:
                self.stream.on_error(e)
                break
        self.stream.on_completed()

    async def close(self):
        self._mic_stream.stop()
        self._mic_stream.close()
        await self._queue.put(None)  # Signal the end of the stream
        
    def start(self):
        try:
            self._mic_stream.start()
        except Exception as e:
            self.stream.on_error(e)
            return False
        finally:
            return True        
        
    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._mic_stream.stopped:
            raise StopAsyncIteration
        try:
            data = await self._queue.get()
            if data is None:
                # None is the signal to stop iteration
                raise StopAsyncIteration
            return data
        except Exception as e:
            self.stream.on_error(e)
            raise StopAsyncIteration
