from arguflow.configuration import Configuration
from arguflow.api_client import ApiClient
from arguflow.api.auth_api import AuthApi
from arguflow.exceptions import ApiException
from arguflow.api.dataset_api import DatasetApi
from arguflow.models.create_dataset_request import CreateDatasetRequest

from logger import logger


class ArguflowManager:
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
                # Bug in the API. Just query the API again...
                dataset_client.create_dataset(create_dataset_request=dataset_request)
                dataset_response = dataset_client.get_datasets_from_organization(
                    organization_id=self.org_id
                )
            logger.debug("Datasets found in the organization")
            return dataset_response[0].dataset.id

        except Exception as e:
            logger.error("Exception when calling AuthApi->get_me: %s\n" % e)
            raise Exception("Error while getting dataset id")

    

arg = ArguflowManager("http://192.168.3.205", 8090, "supersecretkey")
