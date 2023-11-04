import pyaudio
import wave
import threading
import time
import numpy as np
from queue import Queue

class MediaRecorder:
    def __init__(self, rate, channels, width):
        self.rate = rate
        self.channels = channels
        self.width = width
        self.recording = False
        self.frames = []
        self._queue = Queue()
        self._thread = threading.Thread(target=self._record, daemon=True)

    def start(self):
        self.recording = True
        self._thread.start()

    def stop(self):
        self.recording = False
        self._thread.join()

    def add_frame(self, frame):
        self._queue.put(frame)

    def _record(self):
        while self.recording or not self._queue.empty():
            # Every 5 seconds, save the audio to a file
            start_time = time.time()
            self.frames = []

            while time.time() - start_time < 5:
                if not self._queue.empty():
                    frame = self._queue.get()
                    self.frames.append(frame)
                else:
                    time.sleep(0.01)  # Sleep briefly to avoid a busy wait

            self._save_to_file()

    def _save_to_file(self):
        filename = f"recording_{int(time.time())}.wav"
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.width)
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        print(f"Saved: {filename}")

# Usage example:
# recorder = Recorder(rate=44100, channels=2, width=pyaudio.get_sample_size(pyaudio.paInt16))
# recorder.start()
# ... Add frames to the recorder ...
# recorder.add_frame(data)
# ... Once done ...
# recorder.stop()
