import numpy as np
from numpy.typing import NDArray

import torch
import whisper

import faster_whisper.transcribe
from faster_whisper import WhisperModel

from logger import logger

whisper_model = "tiny.en"
model_size = "large-v3"
device = "cuda"
compute_type = "float32"
model = whisper.load_model(whisper_model, device=device)

# faster_whisper.transcribe.Tokenizer.encode = lambda self, text: self.tokenizer.encode(
#     text, add_special_tokens=False
# )
# # Initialize the model outside of the transcribe function
# model = WhisperModel(
#     model_size_or_path=model_size,
#     device=device,
#     compute_type=compute_type,
# )

# # # Monkey patch 3 (change n_mels)
# from faster_whisper.feature_extractor import FeatureExtractor

# model.feature_extractor = FeatureExtractor(feature_size=128)

# # # Monkey patch 4 (change tokenizer)
# from transformers import AutoProcessor

# model.hf_tokenizer = AutoProcessor.from_pretrained("openai/whisper-large-v3").tokenizer
# model.hf_tokenizer.token_to_id = lambda token: model.hf_tokenizer.convert_tokens_to_ids(
#     token
# )


# hard-coded audio hyperparameters
N_FFT = 400
HOP_LENGTH = 160


# Function to run transcription in a separate thread
def transcribe_chunk(audio_chunk: NDArray[np.float32]):
    try:
        logger.debug(
            f"Transcribing chunk of shape: {audio_chunk.shape}, type: {audio_chunk.dtype}"
        )
        # logger.debug("padding audio chunk")
        # audio = whisper.pad_or_trim(audio_chunk)
        # logger.debug("padding complete")
        # logger.debug(f"loading mel spectrogram")
        # mel = whisper.log_mel_spectrogram(audio).to(model.device)
        # logger.debug(f"mel spectrogram loaded")
        # logger.debug("Retrieving decoding options")
        # options = whisper.DecodingOptions()

        # logger.debug("Decoding audio")
        # data = whisper.decode(model, mel, options)
        data = model.transcribe(
            audio_chunk,
            temperature=0.2,
            fp16=torch.cuda.is_available(),
            word_timestamps=True,
        )
        logger.debug(f"Transcribed data: {data}")
        return data
    except Exception as e:
        logger.error(f"Error in transcribe_chunk: {e}")
        raise e
