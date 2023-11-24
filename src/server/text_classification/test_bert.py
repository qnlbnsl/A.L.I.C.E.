import torch
from transformers import BertTokenizer, BertForSequenceClassification
import pandas as pd

# Constants
MODEL_PATH = "trained_bert_model.bin"  # Path to your saved model
MAX_LEN = 128  # Same as used during training
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the tokenizer and model
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=3)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.to(DEVICE)
model.eval()


# Function to preprocess the sentence
def preprocess(sentence):
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
def predict(sentence, model):
    with torch.no_grad():
        inputs = preprocess(sentence)
        input_ids = inputs["input_ids"].to(DEVICE)
        attention_mask = inputs["attention_mask"].to(DEVICE)

        output = model(input_ids, attention_mask=attention_mask)
        _, prediction = torch.max(output.logits, dim=1)

        return prediction.item()


# Mapping of numerical labels back to string labels
label_map = {0: "other", 1: "command", 2: "question"}

# Interactive loop for sentence classification
while True:
    sentence = input("\nEnter a sentence to classify (type 'exit' to quit): ")
    if sentence.lower() == "exit":
        break
    prediction = predict(sentence, model)
    print(f"Predicted Class: {label_map[prediction]}")
