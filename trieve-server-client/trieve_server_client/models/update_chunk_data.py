from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast, Union
from typing import Union






T = TypeVar("T", bound="UpdateChunkData")


@_attrs_define
class UpdateChunkData:
    """ 
        Attributes:
            chunk_uuid (str):
            chunk_html (Union[None, Unset, str]):
            link (Union[None, Unset, str]):
            metadata (Union[Unset, Any]):
            time_stamp (Union[None, Unset, str]):
            tracking_id (Union[None, Unset, str]):
            weight (Union[None, Unset, float]):
     """

    chunk_uuid: str
    chunk_html: Union[None, Unset, str] = UNSET
    link: Union[None, Unset, str] = UNSET
    metadata: Union[Unset, Any] = UNSET
    time_stamp: Union[None, Unset, str] = UNSET
    tracking_id: Union[None, Unset, str] = UNSET
    weight: Union[None, Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        chunk_uuid = self.chunk_uuid

        chunk_html: Union[None, Unset, str]
        if isinstance(self.chunk_html, Unset):
            chunk_html = UNSET
        else:
            chunk_html = self.chunk_html

        link: Union[None, Unset, str]
        if isinstance(self.link, Unset):
            link = UNSET
        else:
            link = self.link

        metadata = self.metadata

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
            "chunk_uuid": chunk_uuid,
        })
        if chunk_html is not UNSET:
            field_dict["chunk_html"] = chunk_html
        if link is not UNSET:
            field_dict["link"] = link
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
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
        chunk_uuid = d.pop("chunk_uuid")

        def _parse_chunk_html(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        chunk_html = _parse_chunk_html(d.pop("chunk_html", UNSET))


        def _parse_link(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        link = _parse_link(d.pop("link", UNSET))


        metadata = d.pop("metadata", UNSET)

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


        update_chunk_data = cls(
            chunk_uuid=chunk_uuid,
            chunk_html=chunk_html,
            link=link,
            metadata=metadata,
            time_stamp=time_stamp,
            tracking_id=tracking_id,
            weight=weight,
        )

        update_chunk_data.additional_properties = d
        return update_chunk_data

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
