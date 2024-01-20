from typing import Self
from enum import Enum
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams


class QdrantDistance(Enum):
    """Type Alias for Qdrant Distance"""

    DOT = "dot"
    COSINE = "cosine"
    EUCLID = "euclid"
    MANHATTAN = "manhattan"


class QdrantManager:
    def __init__(self: Self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.client = QdrantClient(host=host, port=port)

    class Collection:
        def __init__(self: Self, client: QdrantClient) -> None:
            self.client = client

        def create(
            self: Self,
            collection_name: str,
            vector_size: int,
            qdr_distance: QdrantDistance,
        ) -> None:
            distance = Distance.DOT
            if qdr_distance == QdrantDistance.COSINE:
                distance = Distance.COSINE
            elif qdr_distance == QdrantDistance.EUCLID:
                distance = Distance.EUCLID
            elif qdr_distance == QdrantDistance.MANHATTAN:
                distance = Distance.MANHATTAN

            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=distance),
            )

        # list all collections
        # Delete collection

    class Data:
        def __init__(self: Self, client: QdrantClient) -> None:
            self.client = client

        # Add data to collection
        # Retrieve data from collection
        # Update data from collection? (Not sure if this is possible with our use case)
        # Delete data from collection? (why would we need this?)
        
        
        class Search:
            def __init__(self: Self, client: QdrantClient) -> None:
                self.client = client

        class Insert:
            def __init__(self: Self, client: QdrantClient) -> None:
                self.client = client

        class Delete:
            def __init__(self: Self, client: QdrantClient) -> None:
                self.client = client
