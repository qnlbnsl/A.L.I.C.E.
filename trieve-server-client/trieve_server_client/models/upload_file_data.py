from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast, Union
from typing import Union






T = TypeVar("T", bound="UploadFileData")


@_attrs_define
class UploadFileData:
    """ 
        Attributes:
            base64_docx_file (str):
            file_mime_type (str):
            file_name (str):
            create_chunks (Union[None, Unset, bool]):
            description (Union[None, Unset, str]):
            link (Union[None, Unset, str]):
            metadata (Union[Unset, Any]):
            tag_set (Union[None, Unset, str]):
            time_stamp (Union[None, Unset, str]):
     """

    base64_docx_file: str
    file_mime_type: str
    file_name: str
    create_chunks: Union[None, Unset, bool] = UNSET
    description: Union[None, Unset, str] = UNSET
    link: Union[None, Unset, str] = UNSET
    metadata: Union[Unset, Any] = UNSET
    tag_set: Union[None, Unset, str] = UNSET
    time_stamp: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        base64_docx_file = self.base64_docx_file

        file_mime_type = self.file_mime_type

        file_name = self.file_name

        create_chunks: Union[None, Unset, bool]
        if isinstance(self.create_chunks, Unset):
            create_chunks = UNSET
        else:
            create_chunks = self.create_chunks

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

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


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "base64_docx_file": base64_docx_file,
            "file_mime_type": file_mime_type,
            "file_name": file_name,
        })
        if create_chunks is not UNSET:
            field_dict["create_chunks"] = create_chunks
        if description is not UNSET:
            field_dict["description"] = description
        if link is not UNSET:
            field_dict["link"] = link
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if tag_set is not UNSET:
            field_dict["tag_set"] = tag_set
        if time_stamp is not UNSET:
            field_dict["time_stamp"] = time_stamp

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        base64_docx_file = d.pop("base64_docx_file")

        file_mime_type = d.pop("file_mime_type")

        file_name = d.pop("file_name")

        def _parse_create_chunks(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        create_chunks = _parse_create_chunks(d.pop("create_chunks", UNSET))


        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))


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


        upload_file_data = cls(
            base64_docx_file=base64_docx_file,
            file_mime_type=file_mime_type,
            file_name=file_name,
            create_chunks=create_chunks,
            description=description,
            link=link,
            metadata=metadata,
            tag_set=tag_set,
            time_stamp=time_stamp,
        )

        upload_file_data.additional_properties = d
        return upload_file_data

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
