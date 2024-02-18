import os
from typing import List
import uuid
from openai import OpenAI
from trieve_client import AuthenticatedClient
from trieve_client.api.auth import get_me
from trieve_client.api.dataset import get_datasets_from_organization, create_dataset
from trieve_client.models.slim_user import SlimUser
from trieve_client.models.create_dataset_request import CreateDatasetRequest
from trieve_client.models.topic import Topic
from trieve_client.models.dataset import Dataset

from trieve_client.models.error_response_body import ErrorResponseBody


from ..logger import logger

# Card = Chunk = group of text being uploaded, converted to vector, and indexed for search.
# Collection = Index, as in the catalog that keeps track of which set of chunks you are searching in. Right now, a chunk can only be in one collection.
# Page: Trieve paginates chunks, indexes, etc as a way to return a reasonable amount of data rather than try to return 300k chunks.
# Bookmark: this refers to chunks that are indexed (aka card in a collection).


class TrieveManager:
    def __init__(
        self,
        host: str,
        port: int,
        api_key: str,
        openai_api_key: str | None,  # Use the environment variable if not provided
        openai_url: str = "https://api.openai.com/v1",  # Use the default OpenAI API URL if not provided
        org_id: str | None = None,
        dataset_id: str | None = None,
    ) -> None:
        # Trieve Configuration
        self.api_key = api_key  # Required for all API calls
        self.user_id = uuid.UUID("00000000-0000-0000-0000-000000000000")

        # OpenAI Configuration
        if openai_api_key is None:
            openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = OpenAI(api_key=openai_api_key, base_url=openai_url)
        # Trieve API Client
        self.api_client = AuthenticatedClient(
            f"{host}:{port}", prefix="", token=api_key
        )
        self.org_id: str = self._get_org_id() if org_id is None else org_id
        self.dataset_id: str = (
            self._get_dataset_id() if dataset_id is None else dataset_id
        )
        self.api_client.with_headers(
            {
                "TR-Organization": self.org_id,
                "TR-Dataset": self.dataset_id,
            }
        )
        self.topics: List[Topic] = []

    def _get_org_id(self) -> str:
        try:
            # Call the get_me method
            api_response = get_me.sync(client=self.api_client)
            if (
                api_response is None
                or type(api_response) is ErrorResponseBody
                or type(api_response) is not SlimUser
            ):
                raise Exception("Error while getting organization id")

            logger.info("The response of AuthApi->get_me:\n")
            logger.debug(api_response)
            logger.debug(api_response.orgs)

            # TODO: Support for multiple orgs
            if len(api_response.orgs) > 1:
                logger.debug(
                    "User belongs to more than one organization. selecting the first one."
                )
                return api_response.orgs[0].id
            else:
                logger.debug("User belongs to only one organization")
                return api_response.orgs[0].id
        except Exception as e:
            logger.error("Exception when calling AuthApi->get_me: %s\n" % e)
            raise Exception("Error while getting organization id")

    def _get_dataset_id(self) -> str:
        try:
            dataset_response = get_datasets_from_organization.sync(
                client=self.api_client,
                tr_organization=self.org_id,  # Why duplicates?
                organization_id=self.org_id,
            )
            logger.debug(dataset_response)
            if (
                dataset_response is None
                or type(dataset_response) is ErrorResponseBody
                or type(dataset_response) is not list
            ):
                raise Exception("Error while getting dataset id")
            if len(dataset_response) == 0:
                logger.debug("No datasets found in the organization... creating one")
                dataset_request = CreateDatasetRequest(
                    organization_id=self.org_id,
                    dataset_name="Default Dataset",
                    client_configuration=None,
                    server_configuration=None,
                )

                resp = create_dataset.sync(
                    client=self.api_client,
                    body=dataset_request,
                    tr_organization=self.org_id,
                )
                if (
                    resp is None
                    or type(resp) is ErrorResponseBody
                    or type(resp) is not Dataset
                ):
                    raise Exception("Error while creating dataset")
                logger.debug(resp)
                return resp.id
            logger.debug(f"{len(dataset_response)} Datasets found in the organization")
            return dataset_response[0].dataset.id

        except Exception as e:
            logger.error("Exception when calling AuthApi->get_me: %s\n" % e)
            raise Exception("Error while getting dataset id")
