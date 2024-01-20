from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.chunk_collection_and_file import ChunkCollectionAndFile


T = TypeVar("T", bound="CollectionData")


@_attrs_define
class CollectionData:
    """
    Attributes:
        collections (List['ChunkCollectionAndFile']):
        total_pages (int):
    """

    collections: List["ChunkCollectionAndFile"]
    total_pages: int
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        collections = []
        for collections_item_data in self.collections:
            collections_item = collections_item_data.to_dict()
            collections.append(collections_item)

        total_pages = self.total_pages

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "collections": collections,
                "total_pages": total_pages,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.chunk_collection_and_file import ChunkCollectionAndFile

        d = src_dict.copy()
        collections = []
        _collections = d.pop("collections")
        for collections_item_data in _collections:
            collections_item = ChunkCollectionAndFile.from_dict(collections_item_data)

            collections.append(collections_item)

        total_pages = d.pop("total_pages")

        collection_data = cls(
            collections=collections,
            total_pages=total_pages,
        )

        collection_data.additional_properties = d
        return collection_data

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
