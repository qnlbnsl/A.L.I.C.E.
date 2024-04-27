from qdrant_client import models
from nomic import embed


from typing import List

from logger import logger


# Search Query: search_query, search_document, classification, clustering
def process_embeddings(
    texts: List[str],
    model: str = "nomic-embed-text-v1.5",
    task_type: str = "search_query",
) -> models.BatchVectorStruct:
    # Get the embeddings for the given texts.
    # Output: {"embeddings": [], "usage": {}, "model": "model"}
    data = embed.text(
        texts=texts,
        model=model,
        task_type=task_type,
    )
    logger.info(f"Embeddings: {data['embeddings']}")
    return data["embeddings"]  # type: ignore # noqa
