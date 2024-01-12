from multiprocessing import Queue
from multiprocessing.synchronize import Event
from typing import Self
import numpy as np
import re
from numpy.typing import NDArray

from faster_whisper import WhisperModel
from faster_whisper.transcribe import Segment
from stt.wake_word import detect_wake_word, WakeWordBuffer
from logger import logger


class WhisperModelManager:
    def __init__(
        self: Self,
        model_size_or_path: str = "large-v3",
        device: str = "cuda",
        compute_type: str = "float16",
    ):
        self.model_size_or_path = model_size_or_path
        self.device = device
        self.compute_type = compute_type
        self.model = None

        self.word_timestamps = False
        self.initial_prompt = None
        self.wake_word_buffer = WakeWordBuffer()

    def load_model(self: Self) -> None:
        self.model = WhisperModel(
            model_size_or_path=self.model_size_or_path,
            device=self.device,
            compute_type=self.compute_type,
        )

    # Function to run transcription in a separate thread
    def transcribe_chunk(
        self: Self,
        audio_chunk: NDArray[np.float32],
        transcript_queue: "Queue[str]",
        concept_queue: "Queue[Segment]",
        wake_word_event: Event,
    ) -> None:
        try:
            # logger.debug(
            #     f"Transcribing chunk of shape: {audio_chunk.shape}, type: {audio_chunk.dtype}"
            # )
            segments, _ = self.model.transcribe(  # type: ignore # Static analysis is unable to detect the assignment to self.model in load_model
                audio_chunk,
                beam_size=10,
                vad_filter=True,
                word_timestamps=self.word_timestamps,
                temperature=0.0,
                language="en",
                initial_prompt=self.initial_prompt,
            )

            for segment in segments:
                logger.debug(f"Transcribed segment: {segment.text}")
                self.wake_word_buffer.update_buffer(segment)
                concept_queue.put(segment)
                if wake_word_event.is_set() is False:
                    detect_wake_word(
                        self.wake_word_buffer.get_buffer_text(), wake_word_event
                    )
                # Store all transcribed segments in a queue for nightly processing
                if (
                    wake_word_event.is_set()
                    and self.detect_artifacts(segment.text) is False
                ):
                    transcript_queue.put(segment.text)
            # logger.debug(f"Transcribed data: {segments}")

        except Exception as e:
            logger.error(f"Error in transcribe_chunk: {e}")
            raise e

    def detect_artifacts(self: Self, segment_text: str) -> bool:
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
