from trieve_python_client.configuration import Configuration
from trieve_python_client.api_client import ApiClient
from trieve_python_client.api.auth_api import AuthApi
from trieve_python_client.exceptions import ApiException
from trieve_python_client.api.dataset_api import DatasetApi
from trieve_python_client.models.create_dataset_request import CreateDatasetRequest

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
        org_id: str | None = None,
        dataset_id: str | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.api_key = api_key
        self.configuration = Configuration(
            host=self.host + ":" + str(self.port),
        )
        self.configuration.debug = True
        self.configuration.verify_ssl = False
        self.api_client = ApiClient(self.configuration)
        self.org_id: str = self._get_org_id() if org_id is None else org_id
        self.dataset_id: str = (
            self._get_dataset_id() if dataset_id is None else dataset_id
        )
        self.api_client.default_headers = {
            "Authorization": api_key,
            "TR-Dataset": self.dataset_id,
        }

    def _get_org_id(self) -> str:
        self.api_client.default_headers = {"Authorization": self.api_key}
        api_instance = AuthApi(self.api_client)
        try:
            # Call the get_me method
            api_response = api_instance.get_me()
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
        except ApiException as e:
            logger.error("Exception when calling AuthApi->get_me: %s\n" % e)
            raise Exception("Error while getting organization id")

    def _get_dataset_id(self) -> str:
        try:
            self.api_client.default_headers = {
                "Authorization": self.api_key,
                "TR-Organization": self.org_id,
            }
            dataset_client = DatasetApi(self.api_client)
            dataset_response = dataset_client.get_datasets_from_organization(
                organization_id=self.org_id
            )
            logger.debug(dataset_response)
            if len(dataset_response) == 0:
                logger.debug("No datasets found in the organization... creating one")
                dataset_request = CreateDatasetRequest(
                    organization_id=self.org_id,
                    dataset_name="Default Dataset",
                    client_configuration=None,
                    server_configuration=None,
                )

                return dataset_client.create_dataset(
                    create_dataset_request=dataset_request
                ).id
            logger.debug(f"{len(dataset_response)} Datasets found in the organization")
            return dataset_response[0].dataset.id

        except Exception as e:
            logger.error("Exception when calling AuthApi->get_me: %s\n" % e)
            raise Exception("Error while getting dataset id")
