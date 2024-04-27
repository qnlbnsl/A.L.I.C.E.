from .client import Qdrant
from .embeddings import process_embeddings

__all__ = ["Qdrant", "process_embeddings"]


if __name__ == "__main__":
    from logger import logger

    qdrant = Qdrant()

    if "test_collection" not in [c.name for c in qdrant.collections.collections]:
        qdrant.create_collection("test_collection")

    texts = ["What is the best vector database?", "testtttttt"]
    output = process_embeddings(
        texts=texts,
        model="nomic-embed-text-v1.5",
        task_type="search_query",
    )
