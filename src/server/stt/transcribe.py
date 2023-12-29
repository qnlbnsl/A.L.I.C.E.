from multiprocessing import Queue
from multiprocessing.synchronize import Event
import numpy as np
import re
from numpy.typing import NDArray

from faster_whisper import WhisperModel
from faster_whisper.transcribe import Segment
from stt.wake_word import detect_wake_word, WakeWordBuffer
from logger import logger

model_size = "/home/qnlbnsl/ai_voice_assistant/src/server/whisper-large-v3-ct2"
device = "cuda"
compute_type = "int8_float16"

model = WhisperModel(
    model_size_or_path=model_size,
    device=device,
    compute_type=compute_type,
)

word_timestamps = False
initial_prompt = None
wake_word_buffer = WakeWordBuffer()
# Function to run transcription in a separate thread
def transcribe_chunk(
    audio_chunk: NDArray[np.float32], transcript_queue: Queue[str], concept_queue: Queue[Segment], wake_word_event: Event
) -> None:
    try:
        # logger.debug(
        #     f"Transcribing chunk of shape: {audio_chunk.shape}, type: {audio_chunk.dtype}"
        # )
        segments, _ = model.transcribe( # type: ignore # Unknown type inferenced from model.
            audio_chunk,
            beam_size=10,
            vad_filter=True,
            word_timestamps=word_timestamps,
            temperature=0.0,
            language="en",
            initial_prompt=initial_prompt,
        )

        for segment in segments:
            logger.debug(f"Transcribed segment: {segment.text}")
            wake_word_buffer.update_buffer(segment)
            concept_queue.put(segment)
            if wake_word_event.is_set() is False:
                detect_wake_word(wake_word_buffer.get_buffer_text(), wake_word_event)
            # Store all transcribed segments in a queue for nightly processing
            if wake_word_event.is_set() and detect_artifacts(segment.text) is False:
                transcript_queue.put(segment.text)
        # logger.debug(f"Transcribed data: {segments}")

    except Exception as e:
        logger.error(f"Error in transcribe_chunk: {e}")
        raise e

def detect_artifacts(segment_text: str) -> bool:
    # List of suspected artifact strings
    suspected_artifacts = [
        "Subtitles by the Amara.org community",
        "Thank you for watching",
        "Subtitles by the Amara",
        "org community",
        "I'm sorry.",
        "Oh.",
        "Thank you for watching this video.",
        # Add any other suspected artifacts here
    ]

    # Check for lone period or other artifacts
    stripped_text = segment_text.strip()
    if stripped_text == "." or stripped_text in suspected_artifacts:
        return True

    # Check for special characters (like musical notes)
    if "♪" in segment_text:
        return True

    return False