from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from dateutil.parser import isoparse
from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
import datetime
from typing import Union






T = TypeVar("T", bound="ChunkCollectionAndFile")


@_attrs_define
class ChunkCollectionAndFile:
    """ 
        Attributes:
            author_id (str):
            created_at (datetime.datetime):
            description (str):
            id (str):
            name (str):
            updated_at (datetime.datetime):
            file_id (Union[None, Unset, str]):
     """

    author_id: str
    created_at: datetime.datetime
    description: str
    id: str
    name: str
    updated_at: datetime.datetime
    file_id: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        author_id = self.author_id

        created_at = self.created_at.isoformat()

        description = self.description

        id = self.id

        name = self.name

        updated_at = self.updated_at.isoformat()

        file_id: Union[None, Unset, str]
        if isinstance(self.file_id, Unset):
            file_id = UNSET
        else:
            file_id = self.file_id


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "author_id": author_id,
            "created_at": created_at,
            "description": description,
            "id": id,
            "name": name,
            "updated_at": updated_at,
        })
        if file_id is not UNSET:
            field_dict["file_id"] = file_id

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        author_id = d.pop("author_id")

        created_at = isoparse(d.pop("created_at"))




        description = d.pop("description")

        id = d.pop("id")

        name = d.pop("name")

        updated_at = isoparse(d.pop("updated_at"))




        def _parse_file_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        file_id = _parse_file_id(d.pop("file_id", UNSET))


        chunk_collection_and_file = cls(
            author_id=author_id,
            created_at=created_at,
            description=description,
            id=id,
            name=name,
            updated_at=updated_at,
            file_id=file_id,
        )

        chunk_collection_and_file.additional_properties = d
        return chunk_collection_and_file

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
