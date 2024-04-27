# type: ignore
import pandas as pd
from datasets import load_dataset
from IPython.display import Markdown, display_markdown

dataset = load_dataset("heegyu/news-category-dataset", split="train")


def get_single_text(k):
    return f"Under the category:\n{k['category']}:\n{k['headline']}\n{k['short_description']}"


df = pd.DataFrame(dataset)
df.head()

df["year"] = df["date"].dt.year

category_columns_to_keep = [
    "POLITICS",
    "THE WORLDPOST",
    "WORLD NEWS",
    "WORLDPOST",
    "U.S. NEWS",
]

# Filter by category
df_filtered = df[df["category"].isin(category_columns_to_keep)]

# Sample data for each year


def sample_func(x):
    return x.sample(min(len(x), 200), random_state=42)


df_sampled = df_filtered.groupby("year").apply(sample_func).reset_index(drop=True)
df = df_sampled

df["text"] = df.apply(get_single_text, axis=1)
df["text"]


