from typing import Self, cast
import torch
from transformers import (
    DistilBertForSequenceClassification,
    AutoTokenizer,
    AutoModelForSequenceClassification,
    BatchEncoding,
)

from logger import logger
from enums import LABEL_MAP


class TextClassificationModel:
    def __init__(self) -> None:
        # Constants
        self.MODEL_PATH = "qnlbnsl/distilbert_text_classifier"
        self.MAX_LEN = 128  # Same as used during training
        self.DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load the tokenizer and model
        # TODO: change to MODEL_PATH
        self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")  # type: ignore
        self.model = AutoModelForSequenceClassification.from_pretrained(self.MODEL_PATH, num_labels=3, torch_dtype=torch.float16, attn_implementation="flash_attention_2")  # type: ignore
        self.model = cast(DistilBertForSequenceClassification, self.model)  # type: ignore
        # model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        self.model.to(self.DEVICE)  # type: ignore
        self.model.eval()

        logger.info("Text Classification Model Loaded")

    # Function to preprocess the sentence
    def preprocess(self: Self, sentence: str) -> BatchEncoding:
        encoding = self.tokenizer.encode_plus(  # type: ignore
            sentence,
            add_special_tokens=True,
            max_length=self.MAX_LEN,
            return_token_type_ids=False,
            padding="max_length",
            truncation=True,
            return_attention_mask=True,
            return_tensors="pt",
        )
        return encoding

    # Function to predict the class of the sentence
    def classify_sentence(self: Self, sentence: str) -> str:
        with torch.no_grad():
            inputs = self.preprocess(sentence)
            input_ids = cast(BatchEncoding, inputs["input_ids"]).to(self.DEVICE)
            attention_mask = cast(BatchEncoding, inputs["attention_mask"]).to(
                self.DEVICE
            )

            output = self.model(input_ids, attention_mask=attention_mask) # type: ignore
            _, prediction = torch.max(output.logits, dim=1) # type: ignore

            return str(LABEL_MAP[int(prediction.item())])
