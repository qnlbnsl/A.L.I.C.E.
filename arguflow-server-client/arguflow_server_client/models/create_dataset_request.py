from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CreateDatasetRequest")


@_attrs_define
class CreateDatasetRequest:
    """
    Attributes:
        client_configuration (Any):
        dataset_name (str):
        organization_id (str):
        server_configuration (Any):
    """

    client_configuration: Any
    dataset_name: str
    organization_id: str
    server_configuration: Any
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        client_configuration = self.client_configuration

        dataset_name = self.dataset_name

        organization_id = self.organization_id

        server_configuration = self.server_configuration

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "client_configuration": client_configuration,
                "dataset_name": dataset_name,
                "organization_id": organization_id,
                "server_configuration": server_configuration,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        client_configuration = d.pop("client_configuration")

        dataset_name = d.pop("dataset_name")

        organization_id = d.pop("organization_id")

        server_configuration = d.pop("server_configuration")

        create_dataset_request = cls(
            client_configuration=client_configuration,
            dataset_name=dataset_name,
            organization_id=organization_id,
            server_configuration=server_configuration,
        )

        create_dataset_request.additional_properties = d
        return create_dataset_request

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
