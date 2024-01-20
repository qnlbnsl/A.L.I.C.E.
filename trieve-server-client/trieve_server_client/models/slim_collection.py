from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="SlimCollection")


@_attrs_define
class SlimCollection:
    """ 
        Attributes:
            author_id (str):
            id (str):
            name (str):
            of_current_user (bool):
     """

    author_id: str
    id: str
    name: str
    of_current_user: bool
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        author_id = self.author_id

        id = self.id

        name = self.name

        of_current_user = self.of_current_user


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "author_id": author_id,
            "id": id,
            "name": name,
            "of_current_user": of_current_user,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        author_id = d.pop("author_id")

        id = d.pop("id")

        name = d.pop("name")

        of_current_user = d.pop("of_current_user")

        slim_collection = cls(
            author_id=author_id,
            id=id,
            name=name,
            of_current_user=of_current_user,
        )

        slim_collection.additional_properties = d
        return slim_collection

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
