from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.slim_collection import SlimCollection


T = TypeVar("T", bound="BookmarkCollectionResult")


@_attrs_define
class BookmarkCollectionResult:
    """
    Attributes:
        chunk_uuid (str):
        slim_collections (List['SlimCollection']):
    """

    chunk_uuid: str
    slim_collections: List["SlimCollection"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        chunk_uuid = self.chunk_uuid

        slim_collections = []
        for slim_collections_item_data in self.slim_collections:
            slim_collections_item = slim_collections_item_data.to_dict()
            slim_collections.append(slim_collections_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "chunk_uuid": chunk_uuid,
                "slim_collections": slim_collections,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.slim_collection import SlimCollection

        d = src_dict.copy()
        chunk_uuid = d.pop("chunk_uuid")

        slim_collections = []
        _slim_collections = d.pop("slim_collections")
        for slim_collections_item_data in _slim_collections:
            slim_collections_item = SlimCollection.from_dict(slim_collections_item_data)

            slim_collections.append(slim_collections_item)

        bookmark_collection_result = cls(
            chunk_uuid=chunk_uuid,
            slim_collections=slim_collections,
        )

        bookmark_collection_result.additional_properties = d
        return bookmark_collection_result

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
