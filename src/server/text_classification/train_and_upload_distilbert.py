from typing import cast
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    DistilBertTokenizer,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments,
)
from sklearn.metrics import classification_report
from huggingface_hub import notebook_login

# Constants
DISTILBERT = True
MAX_LEN = 128
BATCH_SIZE = 16
EPOCHS = 10

# Hugging Face login
# notebook_login()

# Check if a GPU is available and set PyTorch to use it
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# Dataset Class
class SentenceDataset(Dataset):
    def __init__(self, filename, tokenizer, max_len):
        self.data = pd.read_csv(filename, sep="|")
        print(self.data.head())
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        sentence = self.data.iloc[idx, 1].lower()  # type: ignore
        label = self.data.iloc[idx, 2]
        encoding = self.tokenizer.encode_plus(
            sentence,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding="max_length",
            truncation=True,
            return_attention_mask=True,
            return_tensors="pt",
        )

        return {
            "sentence": sentence,
            "input_ids": encoding["input_ids"].flatten(),
            "attention_mask": encoding["attention_mask"].flatten(),
            "labels": torch.tensor(label, dtype=torch.long),
        }


# Initialize tokenizer
if DISTILBERT:
    tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
    model_class = DistilBertForSequenceClassification
    MODEL_NAME = "distilbert_text_classifier"
else:
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    model_class = BertForSequenceClassification
    MODEL_NAME = "text_classifier_ai_voice_assistant"

# Create Data Loaders
train_dataset = SentenceDataset(
    "/home/qnlbnsl/ai_voice_assistant/src/server/text_classification/training_data/train_pipe.csv",
    tokenizer,
    MAX_LEN,
)
eval_dataset = SentenceDataset(
    "/home/qnlbnsl/ai_voice_assistant/src/server/text_classification/training_data/eval.csv",
    tokenizer,
    MAX_LEN,
)
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
eval_loader = DataLoader(eval_dataset, batch_size=BATCH_SIZE)

# Training Arguments
training_args = TrainingArguments(
    output_dir="./models/results",
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=10,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    hub_model_id=f"qnlbnsl/{MODEL_NAME}",
    load_best_model_at_end=True,  # Load the best model at the end of training
)

# Initialize the model

model = cast(
    DistilBertForSequenceClassification,
    model_class.from_pretrained("distilbert-base-uncased", num_labels=3),
)
model.to(device=device)  # type: ignore

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)

# Training
trainer.train()

# Save the model locally
# trainer.save_model(f"models/{MODEL_NAME}")
# tokenizer.save_pretrained(f"models/{MODEL_NAME}")

# Function to evaluate the model (optional, as Trainer handles evaluation)
def evaluate_model(model, data_loader, device):
    model.eval()

    losses = []
    predictions, true_labels = [], []

    with torch.no_grad():
        for batch in data_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            losses.append(loss.item())

            logits = outputs.logits
            _, preds = torch.max(logits, dim=1)
            predictions.extend(preds)
            true_labels.extend(labels)

    predictions = torch.stack(predictions).cpu()
    true_labels = torch.stack(true_labels).cpu()
    return classification_report(
        true_labels, predictions, target_names=["Question", "Command", "Other"]
    )


# Evaluate the model
report = evaluate_model(model, eval_loader, device)
print(f"Evaluation Report:\n{report}")

print("Saving model to Hugging Face Hub...")
trainer.push_to_hub()
tokenizer.push_to_hub(f"qnlbnsl/{MODEL_NAME}")