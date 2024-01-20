from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from dateutil.parser import isoparse
import datetime
from typing import cast






T = TypeVar("T", bound="ChunkCollection")


@_attrs_define
class ChunkCollection:
    """ 
        Attributes:
            author_id (str):
            created_at (datetime.datetime):
            dataset_id (str):
            description (str):
            id (str):
            name (str):
            updated_at (datetime.datetime):
     """

    author_id: str
    created_at: datetime.datetime
    dataset_id: str
    description: str
    id: str
    name: str
    updated_at: datetime.datetime
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        author_id = self.author_id

        created_at = self.created_at.isoformat()

        dataset_id = self.dataset_id

        description = self.description

        id = self.id

        name = self.name

        updated_at = self.updated_at.isoformat()


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "author_id": author_id,
            "created_at": created_at,
            "dataset_id": dataset_id,
            "description": description,
            "id": id,
            "name": name,
            "updated_at": updated_at,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        author_id = d.pop("author_id")

        created_at = isoparse(d.pop("created_at"))




        dataset_id = d.pop("dataset_id")

        description = d.pop("description")

        id = d.pop("id")

        name = d.pop("name")

        updated_at = isoparse(d.pop("updated_at"))




        chunk_collection = cls(
            author_id=author_id,
            created_at=created_at,
            dataset_id=dataset_id,
            description=description,
            id=id,
            name=name,
            updated_at=updated_at,
        )

        chunk_collection.additional_properties = d
        return chunk_collection

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
