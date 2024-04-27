import os
from qdrant_client import QdrantClient, models
from qdrant_client.models import VectorParams, Distance, CollectionsResponse
from llama_index.core import VectorStoreIndex, ServiceContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.base.response.schema import RESPONSE_TYPE
from llama_index.core.schema import QueryType
from llama_index.core.llms.llm import LLM
from llama_index.core.llms.utils import LLMType
from llama_index.llms.openai import OpenAI


# from .utils import get_file_metadata
from typing import Any, Dict
from logger import logger


class llama_qdrant:
    """
    A class representing a Qdrant client for managing collections and performing queries.

    Args:
        host (str, optional): The host address of the Qdrant server. Defaults to "localhost".
        port (int, optional): The port number of the Qdrant server. Defaults to 6333.
        llm_base_api (str, optional): The base API URL for the OpenAI compatible service. Defaults to .
        llm_base_url (str, optional): The base URL for the OpenAI compatible service. Defaults to .

    Attributes:
        qdrant_client (QdrantClient): The Qdrant client instance.
        collections (CollectionsResponse): The collections retrieved from the Qdrant client.
        service_context (ServiceContext): The service context with default settings for llamaindex.
        _vector_stores (Dict[str, QdrantVectorStore]): The caches for vector stores.
        _indices (Dict[str, VectorStoreIndex]): The caches for indices.

    Methods:
        get_collections: Retrieves the collections from the Qdrant client.
        get_vector_store: Get the vector store for a given collection name.
        get_index: Retrieves the VectorStoreIndex for the given collection name.
        collection_exists: Check if a collection with the given name exists.
        create_collection: Create a new collection in the Qdrant client.
        create_multi_vector_collection: Create a multi-vector collection with the given parameters.
        upload_document: Uploads documents to the specified collection.
        query: Executes a query on the specified collection.
    """

    def __init__(
        self,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        llm_base_api: str = "http://localhost:1234/v1",
        llm_base_url: str = "http://localhost:1234/v1",
    ):
        # Initialize Qdrant client
        if os.getenv("LOCAL") == "True":
            self.qdrant_client = QdrantClient(":memory:")
        else:
            self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)
        # Retrieve collections
        self.collections = self.get_collections()
        # Initialize service context with default settings for llamaindex
        self.service_context = ServiceContext.from_defaults(chunk_size_limit=512)  # type: ignore
        # Initialize caches for vector stores and indices
        self._vector_stores: Dict[str, QdrantVectorStore] = {}  # lazy load as needed
        self._indices: Dict[str, VectorStoreIndex] = {}  # lazy load as needed
        self.llm = self.get_llm()

    # Utility function to retrieve collections
    def get_collections(self) -> CollectionsResponse:
        """
        Retrieves the collections from the Qdrant client.

        Returns:
            A `CollectionsResponse` object containing the collections.
        """
        return self.qdrant_client.get_collections()

    # Utility function to retrieve vector store
    def get_vector_store(self, collection_name: str) -> QdrantVectorStore:
        """
        Get the vector store for a given collection name.

        Args:
            collection_name (str): The name of the collection.

        Returns:
            QdrantVectorStore: The vector store for the specified collection.

        Raises:
            ValueError: If the collection does not exist.
        """
        # Lazy-load or retrieve from cache
        if collection_name not in self._vector_stores:
            # Attempt to retrieve collection info to ensure it exists
            if not self.collection_exists(collection_name):
                raise ValueError(f"Collection {collection_name} does not exist.")
            self._vector_stores[collection_name] = QdrantVectorStore(
                qdrant_client=self.qdrant_client, collection_name=collection_name
            )
        return self._vector_stores[collection_name]

    # Utility function to retrieve index
    def get_index(self, collection_name: str) -> VectorStoreIndex:
        """
        Retrieves the VectorStoreIndex for the given collection name.

        If the index does not exist, it creates a new one using the vector store
        associated with the collection name and the service context.

        Args:
            collection_name (str): The name of the collection.

        Returns:
            VectorStoreIndex: The VectorStoreIndex for the given collection name.
        """
        if collection_name not in self._indices:
            self._indices[collection_name] = VectorStoreIndex.from_vector_store(  # type: ignore
                vector_store=self.get_vector_store(collection_name),
                service_context=self.service_context,
            )
        return self._indices[collection_name]

    # Utility function to check if collection exists
    def collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection with the given name exists.

        Args:
            collection_name (str): The name of the collection to check.

        Returns:
            bool: True if the collection exists, False otherwise.
        """
        collections = self.qdrant_client.get_collections()
        return any(
            collection.name == collection_name for collection in collections.collections
        )

    # Utility function to create collection
    def create_collection(
        self,
        collection_name: str,
        dimension: int = 768,
        init_from_collection: str | None = None,
    ) -> None:
        """
        Create a new collection in the Qdrant client.

        Args:
            collection_name (str): The name of the collection to be created.
            dimension (int, optional): The dimension of the vectors in the collection. Defaults to 768.
            init_from_collection (str | None, optional): The name of an existing collection to initialize from. Defaults to None.

        Raises:
            Exception: If the collection creation fails.

        Returns:
            None
        """
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

    # Utility function to create multi vector collection
    def create_multi_vector_collection(
        self,
        collection_name: str,
        params: VectorParams,
        init_from_collection: str | None = None,
    ) -> None:
        """
        Create a multi-vector collection with the given parameters.

        Args:
            collection_name (str): The name of the collection to be created.
            params (VectorParams): The vector parameters for the collection.
            init_from_collection (str | None, optional): The name of the collection to initialize from.
                Defaults to None.

        Raises:
            Exception: If the collection creation fails.

        Returns:
            None: This method does not return anything.
        """
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

    def get_llm(
        self, base_url: str, api_base: str, api_key: str, temperature: int
    ) -> LLM:
        """
        Creates and returns an instance of the LLM class.

        Args:
            base_url (str): The base URL for the OpenAI API.
            api_base (str): The API base for the OpenAI API.
            api_key (str): The API key for authentication.
            temperature (int): The temperature parameter for generating text.

        Returns:
            LLM: An instance of the LLM class.

        """
        return OpenAI(
            base_url=base_url,
            api_base=api_base,
            api_key=api_key,
            temperature=temperature,
        )

    # Utility function to upload documents
    def upload_document(self, collection_name: str, documents: Dict[str, Any]) -> None:
        """
        Uploads documents to the specified collection.

        Args:
            collection_name (str): The name of the collection to upload the documents to.
            documents (Dict[str, Any]): A dictionary containing the documents to upload.

        Returns:
            None
        """
        index = self.get_index(collection_name)
        for doc in documents:
            index.insert(documents[doc])

    # Utility function to query
    def query(
        self, collection_name: str, query: QueryType, llm: LLMType | None = None  # type: ignore
    ) -> None:
        """
        Executes a query on the specified collection.

        Args:
            collection_name (str): The name of the collection to query.
            query (QueryType): The query to execute.
            llm (LLMType | None, optional): The LLM (Language Model) to use for the query. Defaults to None.

        Notes:
            llm is an optional parameter to pass in a language model.\n
            It is of the type LLMType which is a Union of str, BaseLanguageModel, or LLM.\n
            Setting llm="default" will use the default OpenAI model unless openai is not installed in which case it will use LlamaCPP.\n
            Setting llm=None will disable the LLM.\n
            Setting llm="local:<path>?" will use a local model.\n

        Returns:
            RESPONSE_TYPE: The response from the query.

        """
        index = self.get_index(collection_name)
        if llm is not None:
            query_engine = index.as_query_engine(llm=llm)  # type: ignore
        else:
            query_engine = index.as_query_engine(llm=OpenAI(base_url=self.llm.base_url, api_base=self.llm.api_base, api_key=self.llm["api_key"], temperature=0))  # type: ignore
        response = query_engine.query(query)
        logger.info(f"Query response: {response}")
