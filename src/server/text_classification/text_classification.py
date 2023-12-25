from typing import cast
import torch
from transformers import DistilBertForSequenceClassification, AutoTokenizer, AutoModelForSequenceClassification, BatchEncoding
import pandas as pd
from enums import LABEL_MAP

# Constants
MODEL_PATH = "qnlbnsl/distilbert_text_classifier"  # Path to your saved model
MAX_LEN = 128  # Same as used during training
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased") # TODO: change to MODEL_PATH
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH, num_labels=3)
model = cast(DistilBertForSequenceClassification, model)
# model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.to(DEVICE)  # type: ignore 
model.eval()


# Function to preprocess the sentence
def preprocess(sentence) -> BatchEncoding:
    encoding = tokenizer.encode_plus(
        sentence,
        add_special_tokens=True,
        max_length=MAX_LEN,
        return_token_type_ids=False,
        padding="max_length",
        truncation=True,
        return_attention_mask=True,
        return_tensors="pt",
    )
    return encoding


# Function to predict the class of the sentence
def classify_sentence(sentence: str) -> str:
    with torch.no_grad():
        inputs = preprocess(sentence)
        input_ids = cast(BatchEncoding, inputs["input_ids"]).to(DEVICE)
        attention_mask = cast(BatchEncoding,inputs["attention_mask"]).to(DEVICE)

        output = model(input_ids, attention_mask=attention_mask)
        _, prediction = torch.max(output.logits, dim=1)

        return LABEL_MAP[int(prediction.item())]
