import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification, AdamW
from transformers import get_linear_schedule_with_warmup
from sklearn.metrics import classification_report
import numpy as np
from tqdm import tqdm
import os

# Check if a GPU is available and set PyTorch to use it
# device = torch.device("cpu")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
labels_dict = {"question": 2, "command": 1, "other": 0}


class SentenceDataset(Dataset):
    def __init__(self, filename, tokenizer, max_len):
        self.data = pd.read_csv(filename, sep="|")
        print(self.data.head())
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        sentence = self.data.iloc[idx, 1].lower() # type: ignore
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


# Initialize the tokenizer
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

# Set some constants
MAX_LEN = 128  # You can adjust this depending on the average length of your sentences
BATCH_SIZE = 16  # Adjust based on your GPU memory

# Create Data Loaders
train_dataset = SentenceDataset(
    "/home/qnlbnsl/ai_voice_assistant/src/server/text_classification/training_data/train_pipe.csv",
    tokenizer,
    MAX_LEN,
)
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)

eval_dataset = SentenceDataset(
    "/home/qnlbnsl/ai_voice_assistant/src/server/text_classification/training_data/eval.csv",
    tokenizer,
    MAX_LEN,
)
eval_loader = DataLoader(eval_dataset, batch_size=BATCH_SIZE)

model = BertForSequenceClassification.from_pretrained(
    "bert-base-uncased", num_labels=3
)  # Adjust num_labels based on your classification needs
model = model.to(device)  # type: ignore


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


# Training
EPOCHS = 10  # Adjust as needed

# Define the optimizer
optimizer = AdamW(model.parameters(), lr=5e-5, correct_bias=False)

# Total number of training steps is [number of batches] x [number of epochs].
total_steps = len(train_loader) * EPOCHS

# Set up the learning rate scheduler
scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps=0,  # Default value in run_glue.py
    num_training_steps=total_steps,
)

for epoch in range(EPOCHS):
    model.train()
    total_loss = 0

    for batch in tqdm(train_loader, desc=f"Training Epoch {epoch + 1}"):
        model.zero_grad()

        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        total_loss += loss.item()
        loss.backward()

        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)  # type: ignore
        optimizer.step()
        scheduler.step()

    avg_train_loss = total_loss / len(train_loader)
    print(f"Average training loss for Epoch {epoch + 1}: {avg_train_loss}")

    # Evaluate after each epoch
    report = evaluate_model(model, eval_loader, device)
    print(f"Evaluation Report for Epoch {epoch + 1}:\n{report}")

model_save_path = "trained_bert_model.bin"
torch.save(model.state_dict(), model_save_path)
