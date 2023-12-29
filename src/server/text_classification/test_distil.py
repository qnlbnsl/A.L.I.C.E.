from typing import cast
import torch

# Constants
# DISTIL = True
MODEL_NAME = "qnlbnsl/distilbert_text_classifier"  # Replace with your Hugging Face model path
MAX_LEN = 128  # Same as used during training
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# from transformers import AutoTokenizer, AutoModelForSequenceClassification
# tokenizer = AutoTokenizer.from_pretrained("qnlbnsl/distilbert_text_classifier")
# model = AutoModelForSequenceClassification.from_pretrained("qnlbnsl/distilbert_text_classifier")

from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased") 
model = cast(DistilBertForSequenceClassification,DistilBertForSequenceClassification.from_pretrained(MODEL_NAME))

model.to(DEVICE) # type: ignore
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
    print(f"Predicted Class: {label_map[int(prediction)]}")
