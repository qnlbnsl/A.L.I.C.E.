import time
import re
from multiprocessing.synchronize import Event
from faster_whisper.transcribe import Segment

from logger import logger

class WakeWordBuffer:
    def __init__(self, inactivity_threshold=0.5):  # inactivity threshold in seconds
        self.segments = []
        self.last_update_time = None
        self.inactivity_threshold = inactivity_threshold

    def update_buffer(self, new_segment):
        current_time = time.time()
        self._clear_stale_segments(current_time)
        self.segments.append(new_segment)
        self.last_update_time = current_time

    def _clear_stale_segments(self, current_time):
        if self.last_update_time and (current_time - self.last_update_time) > self.inactivity_threshold:
            self.segments.clear()

    def get_buffer_text(self):
        return ' '.join(segment.text for segment in self.segments)

def detect_wake_word(transcription: str, wake_word_event: Event):
    try:
        if re.search(r"\bhey\s+alice\b", transcription, re.IGNORECASE):
            logger.debug("Detected wake word")
            wake_word_event.set()
    except Exception as e:
        logger.error(f"Error in detect_wake_word: {e}")
        raise e