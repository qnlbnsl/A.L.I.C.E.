from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast, Union
from typing import cast, List
from typing import Union






T = TypeVar("T", bound="SearchCollectionsData")


@_attrs_define
class SearchCollectionsData:
    """ 
        Attributes:
            collection_id (str):
            content (str):
            search_type (str):
            date_bias (Union[None, Unset, bool]):
            filters (Union[Unset, Any]):
            link (Union[List[str], None, Unset]):
            page (Union[None, Unset, int]):
            tag_set (Union[List[str], None, Unset]):
     """

    collection_id: str
    content: str
    search_type: str
    date_bias: Union[None, Unset, bool] = UNSET
    filters: Union[Unset, Any] = UNSET
    link: Union[List[str], None, Unset] = UNSET
    page: Union[None, Unset, int] = UNSET
    tag_set: Union[List[str], None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        collection_id = self.collection_id

        content = self.content

        search_type = self.search_type

        date_bias: Union[None, Unset, bool]
        if isinstance(self.date_bias, Unset):
            date_bias = UNSET
        else:
            date_bias = self.date_bias

        filters = self.filters

        link: Union[List[str], None, Unset]
        if isinstance(self.link, Unset):
            link = UNSET
        elif isinstance(self.link, list):
            link = self.link




        else:
            link = self.link

        page: Union[None, Unset, int]
        if isinstance(self.page, Unset):
            page = UNSET
        else:
            page = self.page

        tag_set: Union[List[str], None, Unset]
        if isinstance(self.tag_set, Unset):
            tag_set = UNSET
        elif isinstance(self.tag_set, list):
            tag_set = self.tag_set




        else:
            tag_set = self.tag_set


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "collection_id": collection_id,
            "content": content,
            "search_type": search_type,
        })
        if date_bias is not UNSET:
            field_dict["date_bias"] = date_bias
        if filters is not UNSET:
            field_dict["filters"] = filters
        if link is not UNSET:
            field_dict["link"] = link
        if page is not UNSET:
            field_dict["page"] = page
        if tag_set is not UNSET:
            field_dict["tag_set"] = tag_set

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        collection_id = d.pop("collection_id")

        content = d.pop("content")

        search_type = d.pop("search_type")

        def _parse_date_bias(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        date_bias = _parse_date_bias(d.pop("date_bias", UNSET))


        filters = d.pop("filters", UNSET)

        def _parse_link(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                link_type_0 = cast(List[str], data)

                return link_type_0
            except: # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        link = _parse_link(d.pop("link", UNSET))


        def _parse_page(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        page = _parse_page(d.pop("page", UNSET))


        def _parse_tag_set(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                tag_set_type_0 = cast(List[str], data)

                return tag_set_type_0
            except: # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        tag_set = _parse_tag_set(d.pop("tag_set", UNSET))


        search_collections_data = cls(
            collection_id=collection_id,
            content=content,
            search_type=search_type,
            date_bias=date_bias,
            filters=filters,
            link=link,
            page=page,
            tag_set=tag_set,
        )

        search_collections_data.additional_properties = d
        return search_collections_data

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
