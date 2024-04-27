from datasets import load_dataset

dataset = load_dataset("ag_news", split="train")

id2label = {str(i): label for i, label in enumerate(dataset.features["label"].names)} # type: ignore

from transformers import AutoModel, AutoTokenizer
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained('gpt2')
model = AutoModel.from_pretrained('gpt2')#.to(device) # switch this for GPU

tokenizer.pad_token = tokenizer.eos_token

with torch.no_grad():
    embs = model(**inputs)
    