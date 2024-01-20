# Not Implemented: Objects: Batch Import, Read, Update, Delete, Search
# Needs to be seen if we need to implement Batch Import for ALICE.
# Batching Import: https://https://weaviate.io/developers/weaviate/manage-data/import
# The following are singular operations i.e. they will need the uuid for the item.
# Not sure why we would need them for ALICE as we only need to search for and add data.
# Maybe we can use them for Daisy?
# Read: https://https://weaviate.io/developers/weaviate/manage-data/read
# Update: https://https://weaviate.io/developers/weaviate/manage-data/update
# Delete: https://https://weaviate.io/developers/weaviate/manage-data/delete

import weaviate
import weaviate.classes as wvc
from weaviate.collections.classes.internal import WeaviateReferences
from weaviate.collections.classes.data import DataObject
from weaviate.collections.classes.batch import BatchObjectReturn
import weaviate.collections.classes.types as wcct
import os
from uuid import UUID
from typing import Any, List, Self, Sequence
from logger import logger
from weaviate.types import UUIDS


class WeaviateManager:
    def __init__(
        self: Self,
        remote_uri: str = "weaviate.home.kunalbans.al",
        remote_uri_grpc: str = "grpc.weaviate.home.kunalbans.al",
        local_uri: str = "192.168.1.19",
        local: bool = False,
    ) -> None:
        self.remote_uri = remote_uri
        self.remote_uri_grpc = remote_uri_grpc
        self.local_uri = local_uri
        self.local = local
        self.client = self.connect_to_weaviate()
        self.collections = self.Collection(self.client)

    def connect_to_weaviate(self: Self) -> weaviate.WeaviateClient:
        http_host = self.remote_uri if not self.local else self.local_uri
        http_secure = False if self.local else True
        http_port = 443 if not self.local else 8080
        grpc_host = self.remote_uri_grpc if not self.local else self.local_uri
        grpc_secure = False if self.local else True
        grpc_port = 80 if not self.local else 50051

        return weaviate.connect_to_custom(  # type: ignore # Headers have an unknown type. Known issue with weaviate.
            http_host=http_host,
            http_port=http_port,
            http_secure=http_secure,
            grpc_host=grpc_host,
            grpc_secure=grpc_secure,
            grpc_port=grpc_port,
            timeout=(
                180,
                180,
            ),  # (connect_timeout, read_timeout) in seconds, currently 3 minutes
            headers={
                "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")
            },  # TODO: Implement Auth
        )

    # Subclasses collection to provide CRUD operations on collections
    class Collection:
        def __init__(self: Self, client: weaviate.WeaviateClient) -> None:
            self.client = client

        def create(
            self: Self,
            collection_name: str,
            properties: List[wvc.Property],
            description: str,
        ) -> weaviate.Collection:
            collection = self.client.collections.create(
                name=collection_name,
                vectorizer_config=wvc.Configure.Vectorizer.text2vec_openai(),
                generative_config=wvc.Configure.Generative.openai(),
                properties=properties,
                description=description,
            )
            return collection

        def read(self: Self, collection_name: str) -> weaviate.Collection:
            try:
                if self.client.collections.exists(collection_name):
                    return self.client.collections.get(collection_name)
                else:
                    return self.create(
                        collection_name=collection_name, properties=[], description=""
                    )  # Create empty collection with no properties if it doesn't exist
            except Exception as e:
                logger.error(f"Failed to retrieve collection {collection_name}")
                raise Exception("Failed to retrieve collection with error {e}")

        def update(
            self: Self,
            collection_name: str,
            properties: List[wvc.Property],
            description: str,
        ) -> None:
            if self.client.collections.exists(collection_name):
                col = self.client.collections.get(collection_name)
                if properties != []:
                    # update properties
                    for prop in properties:
                        col.config.add_property(prop)
                if description != "":
                    # update description
                    col.config.update(description=description)

            else:
                logger.debug(f"Collection {collection_name} does not exist")

        def delete(self: Self, collection_name: str) -> None:
            if self.client.collections.exists(collection_name):
                self.client.collections.delete(collection_name)
            else:
                logger.debug(f"Collection {collection_name} does not exist")

        def list(
            self: Self,
        ) -> (
            Any
        ):  # Deliberately Any because weaviate's list_all() returns a Dict with private properties
            return self.client.collections.list_all()

    class Create:
        def __init__(self: Self, client: weaviate.WeaviateClient) -> None:
            self.client = client

        def insert(
            self: Self,
            collection_name: str,
            data: wcct.WeaviateProperties,
            references: WeaviateReferences | None = None,
            vector: List[float] | None = None,
        ) -> tuple[UUID]:
            try:
                uuid = (
                    self.client.collections.get(collection_name).data.insert(
                        properties=data, references=references, vector=vector
                    ),
                )

                return uuid
            except Exception as e:
                logger.error(
                    f"Failed to insert data into collection {collection_name} with error {e}"
                )
                raise Exception(
                    "Failed to insert data into collection with error {e.message}"
                )

        def bulk_insert(
            self: Self,
            collection_name: str,
            objects: Sequence[
                wcct.WeaviateProperties
                | DataObject[wcct.WeaviateProperties, WeaviateReferences | None]
            ],
        ) -> tuple[BatchObjectReturn]:
            try:
                return (
                    self.client.collections.get(collection_name).data.insert_many(
                        objects=objects
                    ),
                )
            except Exception as e:
                logger.error(
                    f"Failed to insert data into collection {collection_name} with error {e}"
                )
                raise Exception(
                    "Failed to insert data into collection with error {e.message}"
                )

    # Ideally should never be used. Should use a multisearch instead and then create the object with the reference included.
    class CrossReference:
        def __init__(self: Self, client: weaviate.WeaviateClient) -> None:
            self.client = client

        def add_reference(
            self: Self,
            source_collection_name: str,
            target_collection_name: str,
            from_property: str,
            to_property: str,
            from_uuid: UUID,
            to_uuid: UUID,
        ) -> None:
            try:
                collection = self.client.collections.get(source_collection_name)
                collection.data.reference_add(
                    from_uuid=from_uuid,
                    from_property=from_property,
                    to=wvc.Reference.to(uuids=[to_uuid]),
                )
            except Exception as e:
                logger.error(
                    f"Failed to add reference to collection {source_collection_name} to {target_collection_name} with error {e}"
                )
                raise Exception(
                    "Failed to add reference to collection with error {e.message}"
                )

        def add_references(
            self: Self,
            source_collection_name: str,
            target_collection_name: str,
            from_property: str,
            from_uuid: UUID,
            to_uuids: UUIDS,
        ) -> None:
            try:
                collection = self.client.collections.get(source_collection_name)
                collection.data.reference_add(
                    from_uuid=from_uuid,
                    from_property=from_property,
                    to=wvc.Reference.to(uuids=to_uuids),
                )
            except Exception as e:
                logger.error(
                    f"Failed to add reference to collection {source_collection_name} to {target_collection_name} with error {e}"
                )
                raise Exception(
                    "Failed to add reference to collection with error {e.message}"
                )

        def add_two_way_reference(
            self: Self,
            source_collection_name: str,
            target_collection_name: str,
            from_property: str,
            to_property: str,
            from_uuid: UUID,
            to_uuid: UUID,
        ) -> None:
            try:
                collection_1 = self.client.collections.get(source_collection_name)
                collection_1.data.reference_add(
                    from_uuid=from_uuid,
                    from_property=from_property,
                    to=wvc.Reference.to(uuids=[to_uuid]),
                )
                collection_2 = self.client.collections.get(source_collection_name)
                collection_2.data.reference_add(
                    from_uuid=to_uuid,
                    from_property=to_property,
                    to=wvc.Reference.to(uuids=[from_uuid]),
                )
            except Exception as e:
                logger.error(
                    f"Failed to add reference to collection {source_collection_name} to {target_collection_name} with error {e}"
                )
                raise Exception("Failed to add reference to collection with error {e}")

    class Search:
        def __init__(self: Self, client: weaviate.WeaviateClient) -> None:
            self.client = client

        def search(self: Self, query: str, filter: List[str]) -> Any:
            try:
                _a = 1
                self.client.collections.get("test").query.hybrid(
                    query=query, filters=wvc.Filter("tags").equal(filter)
                )
            except Exception as e:
                logger.error(f"Failed to search with error {e}")
                raise Exception(f"Failed to search with error {e}")
