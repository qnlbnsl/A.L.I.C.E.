from multiprocessing import Queue
import numpy as np
from numpy.typing import NDArray

from faster_whisper import WhisperModel

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


# Function to run transcription in a separate thread
def transcribe_chunk(
    audio_chunk: NDArray[np.float32], transcript_queue: Queue, concept_queue: Queue
):
    try:
        # logger.debug(
        #     f"Transcribing chunk of shape: {audio_chunk.shape}, type: {audio_chunk.dtype}"
        # )
        segments, _ = model.transcribe(
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
            transcript_queue.put(segment.text)
            concept_queue.put(segment)
        # logger.debug(f"Transcribed data: {segments}")

    except Exception as e:
        logger.error(f"Error in transcribe_chunk: {e}")
        raise e
