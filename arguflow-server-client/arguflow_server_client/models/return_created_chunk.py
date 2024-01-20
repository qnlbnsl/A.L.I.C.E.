from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.chunk_metadata import ChunkMetadata


T = TypeVar("T", bound="ReturnCreatedChunk")


@_attrs_define
class ReturnCreatedChunk:
    """
    Attributes:
        chunk_metadata (ChunkMetadata):
        duplicate (bool):
    """

    chunk_metadata: "ChunkMetadata"
    duplicate: bool
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        chunk_metadata = self.chunk_metadata.to_dict()

        duplicate = self.duplicate

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "chunk_metadata": chunk_metadata,
                "duplicate": duplicate,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.chunk_metadata import ChunkMetadata

        d = src_dict.copy()
        chunk_metadata = ChunkMetadata.from_dict(d.pop("chunk_metadata"))

        duplicate = d.pop("duplicate")

        return_created_chunk = cls(
            chunk_metadata=chunk_metadata,
            duplicate=duplicate,
        )

        return_created_chunk.additional_properties = d
        return return_created_chunk

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
