from typing import Self
from arguflow_server_client import AuthenticatedClient
from arguflow_server_client.api.auth import get_me

# from arguflow_server_client.api.dataset import get_datasets_from_organization
# from arguflow_server_client.api.organization import get_organization


class ArguflowManager:
    def __init__(self: Self, url: str, token: str) -> None:
        self.client = AuthenticatedClient(
            url,
            token=token,
            prefix="",
        )
        # self.org_client = self.client.with_headers(
        #     {"TR-Organization": self.get_org_id()}
        # )
        # self.dataset_client = self.client.with_headers(
        #     {"TR-Dataset": self.get_dataset_id()}
        # )

    def get_org_id(self: Self) -> str:
        resp = get_me.sync_detailed(client=self.client)
        print(resp)
        return "str(resp)"
        # return resp.id

    # def get_dataset_id(self: Self) -> str:
    #     resp = get_datasets_from_organization.sync(
    #         client=self.org_client, organization_id=self.get_org_id()
    #     )
    #     print(resp)
    #     return resp.dataset_id


data = ArguflowManager(url="http://docker-standalone:8090", token="supersecretkey")
data.get_org_id()
# Available modules:
# auth, chunk, chunk_collection, dataset, file, health, message, notifications, organization, topic, user
