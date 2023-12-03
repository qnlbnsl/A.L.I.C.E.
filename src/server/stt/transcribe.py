import numpy as np
from numpy.typing import NDArray

# import torch
# import whisper

# import faster_whisper.transcribe
from faster_whisper import WhisperModel

from logger import logger

whisper_model = "tiny.en"
model_size = "/home/qnlbnsl/ai_voice_assistant/src/server/whisper-large-v3-ct2"
device = "cuda"
compute_type = "int8_float16"
# model = whisper.load_model(whisper_model, device=device)

# faster_whisper.transcribe.Tokenizer.encode = lambda self, text: self.tokenizer.encode(
#     text, add_special_tokens=False
# )
# # Initialize the model outside of the transcribe function
model = WhisperModel(
    model_size_or_path=model_size,
    device=device,
    compute_type=compute_type,
)

# # # Monkey patch 3 (change n_mels)
# from faster_whisper.feature_extractor import FeatureExtractor

# model.feature_extractor = FeatureExtractor(feature_size=128)

# # # Monkey patch 4 (change tokenizer)
# from transformers import AutoProcessor

# model.hf_tokenizer = AutoProcessor.from_pretrained("openai/whisper-large-v3").tokenizer
# model.hf_tokenizer.token_to_id = lambda token: model.hf_tokenizer.convert_tokens_to_ids(
#     token
# )

word_timestamps = False
initial_prompt = None


# Function to run transcription in a separate thread
def transcribe_chunk(audio_chunk: NDArray[np.float32]):
    try:
        # logger.debug(
        #     f"Transcribing chunk of shape: {audio_chunk.shape}, type: {audio_chunk.dtype}"
        # )
        segments, info = model.transcribe(
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
        # logger.debug(f"Transcribed data: {segments}")
        # return data
    except Exception as e:
        logger.error(f"Error in transcribe_chunk: {e}")
        raise e
