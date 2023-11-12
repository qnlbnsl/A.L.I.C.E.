import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
from faster_whisper import WhisperModel
import numpy as np
import faster_whisper.transcribe

from stt.circular_buffer import CircularBuffer

from logger import logger

model_path = "turicas/faster-whisper-large-v3"
prepped_audio_queue = asyncio.Queue()
initial_prompt = None  # Or `None`
word_timestamps = False
device, compute_type = "cuda", "float16"

faster_whisper.transcribe.Tokenizer.encode = lambda self, text: self.tokenizer.encode(
    text, add_special_tokens=False
)
# Initialize the model outside of the transcribe function
model = WhisperModel(
    model_size_or_path=model_path,
    device=device,
    compute_type=compute_type,
)

# Monkey patch 3 (change n_mels)
from faster_whisper.feature_extractor import FeatureExtractor

model.feature_extractor = FeatureExtractor(feature_size=128)

# Monkey patch 4 (change tokenizer)
from transformers import AutoProcessor

model.hf_tokenizer = AutoProcessor.from_pretrained("openai/whisper-large-v3").tokenizer
model.hf_tokenizer.token_to_id = lambda token: model.hf_tokenizer.convert_tokens_to_ids(
    token
)


MAX_BUFFER_DURATION = 3  # seconds
# Initialize the circular buffer
circular_buffer = CircularBuffer(capacity=MAX_BUFFER_DURATION, sample_rate=16000)


# Function to run transcription in a separate thread
def transcribe_chunk(audio_chunk):
    # logger.debug(f"Transcribing chunk of shape: {audio_chunk.shape}")
    # First, convert audio_chunk from int16 to float32
    audio_chunk = audio_chunk.astype(np.float32)
    # Normalize the float32 audio data to range from -1 to 1
    audio_chunk /= np.iinfo(np.int16).max
    # Now audio_chunk_resampled is an np.ndarray[float32] with values ranging from -1 to 1 and resampled to 16kHz
    segments, info = model.transcribe(
        audio_chunk,
        beam_size=8,
        vad_filter=True,
        word_timestamps=word_timestamps,
        temperature=0.0,
        language="en",
        initial_prompt=initial_prompt,
    )
    return segments, info


async def transcribe():
    try:
        # Create a ThreadPoolExecutor for running transcription tasks
        with ThreadPoolExecutor() as executor:
            while True:
                # logger.debug("Waiting for audio chunk")
                data = await prepped_audio_queue.get()
                # logger.debug(f"Got audio chunk of shape: {data.shape}")
                # logger.debug(f"Writing audio chunk to buffer")
                await circular_buffer.write(data)
                # logger.debug(f"Audio chunk written to buffer")
                # If buffer is full , transcribe it
                buffer_duration = circular_buffer.get_buffer_duration()

                # logger.debug("Buffer duration: " + str(buffer_duration))

                if buffer_duration >= MAX_BUFFER_DURATION:
                    # logger.debug("Buffer is full, transcribing")
                    audio_chunk = await circular_buffer.read(MAX_BUFFER_DURATION)
                    if audio_chunk is not None:
                        # Run the transcription in a separate thread
                        loop = asyncio.get_running_loop()
                        future = loop.run_in_executor(
                            executor, transcribe_chunk, audio_chunk
                        )
                        (
                            segments,
                            info,
                        ) = await future  # Wait for the transcription to complete

                        # Process the transcribed segments
                        start_time = time.time()
                        for segment in segments:
                            row = {
                                "start": segment.start,
                                "end": segment.end,
                                "text": segment.text,
                            }
                            if word_timestamps:
                                row["words"] = [
                                    {
                                        "start": word.start,
                                        "end": word.end,
                                        "word": word.word,
                                    }
                                    for word in segment.words
                                ]
                            print(row)
                        end_time = time.time()
                        duration = end_time - start_time
                        # logger.debug(f"Processed segments in {duration} seconds")
    except Exception as e:
        logger.error(f"Error in transcribe: {e}")
        raise e


# # Example usage
# prepped_audio_queue = asyncio.Queue()
# # Assume another part of the application is putting audio chunks into prepped_audio_queue
# asyncio.run(transcribe(prepped_audio_queue))
