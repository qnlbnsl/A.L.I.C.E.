from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast, Union
from typing import cast, List
from typing import Union






T = TypeVar("T", bound="CreateChunkData")


@_attrs_define
class CreateChunkData:
    """ 
        Attributes:
            chunk_html (Union[None, Unset, str]):
            chunk_vector (Union[List[float], None, Unset]):
            collection_id (Union[None, Unset, str]):
            file_uuid (Union[None, Unset, str]):
            link (Union[None, Unset, str]):
            metadata (Union[Unset, Any]):
            tag_set (Union[None, Unset, str]):
            time_stamp (Union[None, Unset, str]):
            tracking_id (Union[None, Unset, str]):
            weight (Union[None, Unset, float]):
     """

    chunk_html: Union[None, Unset, str] = UNSET
    chunk_vector: Union[List[float], None, Unset] = UNSET
    collection_id: Union[None, Unset, str] = UNSET
    file_uuid: Union[None, Unset, str] = UNSET
    link: Union[None, Unset, str] = UNSET
    metadata: Union[Unset, Any] = UNSET
    tag_set: Union[None, Unset, str] = UNSET
    time_stamp: Union[None, Unset, str] = UNSET
    tracking_id: Union[None, Unset, str] = UNSET
    weight: Union[None, Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        chunk_html: Union[None, Unset, str]
        if isinstance(self.chunk_html, Unset):
            chunk_html = UNSET
        else:
            chunk_html = self.chunk_html

        chunk_vector: Union[List[float], None, Unset]
        if isinstance(self.chunk_vector, Unset):
            chunk_vector = UNSET
        elif isinstance(self.chunk_vector, list):
            chunk_vector = self.chunk_vector




        else:
            chunk_vector = self.chunk_vector

        collection_id: Union[None, Unset, str]
        if isinstance(self.collection_id, Unset):
            collection_id = UNSET
        else:
            collection_id = self.collection_id

        file_uuid: Union[None, Unset, str]
        if isinstance(self.file_uuid, Unset):
            file_uuid = UNSET
        else:
            file_uuid = self.file_uuid

        link: Union[None, Unset, str]
        if isinstance(self.link, Unset):
            link = UNSET
        else:
            link = self.link

        metadata = self.metadata

        tag_set: Union[None, Unset, str]
        if isinstance(self.tag_set, Unset):
            tag_set = UNSET
        else:
            tag_set = self.tag_set

        time_stamp: Union[None, Unset, str]
        if isinstance(self.time_stamp, Unset):
            time_stamp = UNSET
        else:
            time_stamp = self.time_stamp

        tracking_id: Union[None, Unset, str]
        if isinstance(self.tracking_id, Unset):
            tracking_id = UNSET
        else:
            tracking_id = self.tracking_id

        weight: Union[None, Unset, float]
        if isinstance(self.weight, Unset):
            weight = UNSET
        else:
            weight = self.weight


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if chunk_html is not UNSET:
            field_dict["chunk_html"] = chunk_html
        if chunk_vector is not UNSET:
            field_dict["chunk_vector"] = chunk_vector
        if collection_id is not UNSET:
            field_dict["collection_id"] = collection_id
        if file_uuid is not UNSET:
            field_dict["file_uuid"] = file_uuid
        if link is not UNSET:
            field_dict["link"] = link
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if tag_set is not UNSET:
            field_dict["tag_set"] = tag_set
        if time_stamp is not UNSET:
            field_dict["time_stamp"] = time_stamp
        if tracking_id is not UNSET:
            field_dict["tracking_id"] = tracking_id
        if weight is not UNSET:
            field_dict["weight"] = weight

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        def _parse_chunk_html(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        chunk_html = _parse_chunk_html(d.pop("chunk_html", UNSET))


        def _parse_chunk_vector(data: object) -> Union[List[float], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                chunk_vector_type_0 = cast(List[float], data)

                return chunk_vector_type_0
            except: # noqa: E722
                pass
            return cast(Union[List[float], None, Unset], data)

        chunk_vector = _parse_chunk_vector(d.pop("chunk_vector", UNSET))


        def _parse_collection_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        collection_id = _parse_collection_id(d.pop("collection_id", UNSET))


        def _parse_file_uuid(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        file_uuid = _parse_file_uuid(d.pop("file_uuid", UNSET))


        def _parse_link(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        link = _parse_link(d.pop("link", UNSET))


        metadata = d.pop("metadata", UNSET)

        def _parse_tag_set(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        tag_set = _parse_tag_set(d.pop("tag_set", UNSET))


        def _parse_time_stamp(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        time_stamp = _parse_time_stamp(d.pop("time_stamp", UNSET))


        def _parse_tracking_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        tracking_id = _parse_tracking_id(d.pop("tracking_id", UNSET))


        def _parse_weight(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        weight = _parse_weight(d.pop("weight", UNSET))


        create_chunk_data = cls(
            chunk_html=chunk_html,
            chunk_vector=chunk_vector,
            collection_id=collection_id,
            file_uuid=file_uuid,
            link=link,
            metadata=metadata,
            tag_set=tag_set,
            time_stamp=time_stamp,
            tracking_id=tracking_id,
            weight=weight,
        )

        create_chunk_data.additional_properties = d
        return create_chunk_data

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
