import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="FileUploadCompletedNotificationWithName")


@_attrs_define
class FileUploadCompletedNotificationWithName:
    """
    Attributes:
        collection_uuid (str):
        created_at (datetime.datetime):
        id (str):
        updated_at (datetime.datetime):
        user_read (bool):
        user_uuid (str):
        collection_name (Union[None, Unset, str]):
    """

    collection_uuid: str
    created_at: datetime.datetime
    id: str
    updated_at: datetime.datetime
    user_read: bool
    user_uuid: str
    collection_name: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        collection_uuid = self.collection_uuid

        created_at = self.created_at.isoformat()

        id = self.id

        updated_at = self.updated_at.isoformat()

        user_read = self.user_read

        user_uuid = self.user_uuid

        collection_name: Union[None, Unset, str]
        if isinstance(self.collection_name, Unset):
            collection_name = UNSET
        else:
            collection_name = self.collection_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "collection_uuid": collection_uuid,
                "created_at": created_at,
                "id": id,
                "updated_at": updated_at,
                "user_read": user_read,
                "user_uuid": user_uuid,
            }
        )
        if collection_name is not UNSET:
            field_dict["collection_name"] = collection_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        collection_uuid = d.pop("collection_uuid")

        created_at = isoparse(d.pop("created_at"))

        id = d.pop("id")

        updated_at = isoparse(d.pop("updated_at"))

        user_read = d.pop("user_read")

        user_uuid = d.pop("user_uuid")

        def _parse_collection_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        collection_name = _parse_collection_name(d.pop("collection_name", UNSET))

        file_upload_completed_notification_with_name = cls(
            collection_uuid=collection_uuid,
            created_at=created_at,
            id=id,
            updated_at=updated_at,
            user_read=user_read,
            user_uuid=user_uuid,
            collection_name=collection_name,
        )

        file_upload_completed_notification_with_name.additional_properties = d
        return file_upload_completed_notification_with_name

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
