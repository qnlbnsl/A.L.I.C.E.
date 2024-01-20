from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast, List
from typing import cast
from typing import Dict

if TYPE_CHECKING:
  from ..models.score_chunk_dto import ScoreChunkDTO
  from ..models.chunk_collection import ChunkCollection





T = TypeVar("T", bound="SearchCollectionsResult")


@_attrs_define
class SearchCollectionsResult:
    """ 
        Attributes:
            bookmarks (List['ScoreChunkDTO']):
            collection (ChunkCollection):
            total_pages (int):
     """

    bookmarks: List['ScoreChunkDTO']
    collection: 'ChunkCollection'
    total_pages: int
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.score_chunk_dto import ScoreChunkDTO
        from ..models.chunk_collection import ChunkCollection
        bookmarks = []
        for bookmarks_item_data in self.bookmarks:
            bookmarks_item = bookmarks_item_data.to_dict()
            bookmarks.append(bookmarks_item)





        collection = self.collection.to_dict()

        total_pages = self.total_pages


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "bookmarks": bookmarks,
            "collection": collection,
            "total_pages": total_pages,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.score_chunk_dto import ScoreChunkDTO
        from ..models.chunk_collection import ChunkCollection
        d = src_dict.copy()
        bookmarks = []
        _bookmarks = d.pop("bookmarks")
        for bookmarks_item_data in (_bookmarks):
            bookmarks_item = ScoreChunkDTO.from_dict(bookmarks_item_data)



            bookmarks.append(bookmarks_item)


        collection = ChunkCollection.from_dict(d.pop("collection"))




        total_pages = d.pop("total_pages")

        search_collections_result = cls(
            bookmarks=bookmarks,
            collection=collection,
            total_pages=total_pages,
        )

        search_collections_result.additional_properties = d
        return search_collections_result

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
