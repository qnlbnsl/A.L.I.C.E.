from qdrant_client import QdrantClient, models
from qdrant_client.models import VectorParams, Distance, CollectionsResponse

import datetime
import os
import random
from pathlib import Path
from glob import glob
from llama_index.core import VectorStoreIndex, ServiceContext, SimpleDirectoryReader
from llama_index.core.postprocessor import FixedRecencyPostprocessor
from llama_index.postprocessor.cohere_rerank import CohereRerank
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import Settings

from .utils import get_file_metadata
from typing import List, Any, Dict

# qdrant_client = QdrantClient("localhost", port=6333)

from logger import logger


class Qdrant:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        cohere_api_key: str | None = None,
    ):
        Settings.embed_model = "default"
        Settings.
        self.qdrant_client = QdrantClient(host, port=port)
        self.collections = self.get_collections()
        self._vector_stores: Dict[str, QdrantVectorStore] = {}
        self.service_context = ServiceContext.from_defaults(chunk_size_limit=512)  # type: ignore

    def get_collections(self) -> CollectionsResponse:
        return self.qdrant_client.get_collections()

    def get_vector_store(self, collection_name: str) -> QdrantVectorStore:
        # Lazy-load or retrieve from cache
        if collection_name not in self._vector_stores:
            # Attempt to retrieve collection info to ensure it exists
            if not self.collection_exists(collection_name):
                raise ValueError(f"Collection {collection_name} does not exist.")
            self._vector_stores[collection_name] = QdrantVectorStore(
                qdrant_client=self.qdrant_client, collection_name=collection_name
            )
        return self._vector_stores[collection_name]

    def collection_exists(self, collection_name: str) -> bool:
        collections = self.qdrant_client.get_collections()
        return any(
            collection.name == collection_name for collection in collections.collections
        )

    def create_collection(
        self,
        collection_name: str,
        dimension: int = 768,
        init_from_collection: str | None = None,
    ) -> None:
        init_from_param = (
            None
            if init_from_collection is None
            else models.InitFrom(collection=init_from_collection)
        )
        success = self.qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
            init_from=init_from_param,
        )
        if success:
            logger.info(f"Collection {collection_name} created successfully.")
        else:
            logger.error(f"Collection {collection_name} creation failed.")
            raise Exception(f"Collection {collection_name} creation failed.")

    def create_multi_vector_collection(
        self,
        collection_name: str,
        params: VectorParams,
        init_from_collection: str | None = None,
    ) -> None:
        init_from_param = (
            None
            if init_from_collection is None
            else models.InitFrom(collection=init_from_collection)
        )
        success = self.qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=params,
            init_from=init_from_param,
        )
        if success:
            logger.info(f"Collection {collection_name} created successfully.")
        else:
            logger.error(f"Collection {collection_name} creation failed.")
            raise Exception(f"Collection {collection_name} creation failed.")

    # def search(
    #     self,
    #     collection_name: str,
    #     query: str,
    #     limit: int = 10,
    #     filter: models.Filter | None = None,
    #     search_params: models.SearchParams | None = None,
    # ) -> List[models.Payload]:
    #     encoded_query = self.sentence_transformer(query).tolist()
    #     res = self.qdrant_client.search(
    #         collection_name=collection_name,
    #         query_vector=encoded_query,
    #         query_filter=filter,
    #         limit=limit,
    #         search_params=search_params,
    #     )
    #     data: List[models.Payload] = []
    #     for r in res:
    #         logger.info(f"Search result: {r}")
    #         if r.payload is not None:
    #             data.append(r.payload)
    #     return data

    def upload_docs(self, docs_dir: str, collection_name: str) -> None:
        docs = glob(f"{Path(docs_dir).resolve()}/*.*")

        documents = SimpleDirectoryReader(
            input_files=docs, file_metadata=get_file_metadata
        ).load_data()

        index = VectorStoreIndex.from_documents(
            documents,
            vector_store=self.get_vector_store(collection_name=collection_name),
            service_context=self.service_context,
        )
        VectorStoreIndex.from_vector_store(  # type: ignore
            vector_store=self.get_vector_store(collection_name=collection_name),
            service_context=self.service_context,
        )
