from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateTopicData")


@_attrs_define
class CreateTopicData:
    """
    Attributes:
        name (str):
        normal_chat (Union[None, Unset, bool]):
    """

    name: str
    normal_chat: Union[None, Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        normal_chat: Union[None, Unset, bool]
        if isinstance(self.normal_chat, Unset):
            normal_chat = UNSET
        else:
            normal_chat = self.normal_chat

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if normal_chat is not UNSET:
            field_dict["normal_chat"] = normal_chat

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        def _parse_normal_chat(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        normal_chat = _parse_normal_chat(d.pop("normal_chat", UNSET))

        create_topic_data = cls(
            name=name,
            normal_chat=normal_chat,
        )

        create_topic_data.additional_properties = d
        return create_topic_data

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
