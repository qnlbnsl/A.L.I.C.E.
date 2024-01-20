from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast, Union
from typing import Union






T = TypeVar("T", bound="GenerateOffCollectionData")


@_attrs_define
class GenerateOffCollectionData:
    """ 
        Attributes:
            collection_id (str):
            page (Union[None, Unset, int]):
            query (Union[None, Unset, str]):
     """

    collection_id: str
    page: Union[None, Unset, int] = UNSET
    query: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        collection_id = self.collection_id

        page: Union[None, Unset, int]
        if isinstance(self.page, Unset):
            page = UNSET
        else:
            page = self.page

        query: Union[None, Unset, str]
        if isinstance(self.query, Unset):
            query = UNSET
        else:
            query = self.query


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "collection_id": collection_id,
        })
        if page is not UNSET:
            field_dict["page"] = page
        if query is not UNSET:
            field_dict["query"] = query

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        collection_id = d.pop("collection_id")

        def _parse_page(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        page = _parse_page(d.pop("page", UNSET))


        def _parse_query(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        query = _parse_query(d.pop("query", UNSET))


        generate_off_collection_data = cls(
            collection_id=collection_id,
            page=page,
            query=query,
        )

        generate_off_collection_data.additional_properties = d
        return generate_off_collection_data

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
