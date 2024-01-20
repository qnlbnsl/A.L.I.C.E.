from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Dict
from ..types import UNSET, Unset
from typing import cast, List
from typing import cast
from typing import cast, Union
from typing import Union

if TYPE_CHECKING:
  from ..models.search_chunk_data_weights_type_0_item import SearchChunkDataWeightsType0Item
  from ..models.search_chunk_data_time_range_type_0_item import SearchChunkDataTimeRangeType0Item





T = TypeVar("T", bound="SearchChunkData")


@_attrs_define
class SearchChunkData:
    """ 
        Attributes:
            content (str):
            search_type (str):
            cross_encoder (Union[None, Unset, bool]):
            date_bias (Union[None, Unset, bool]):
            filters (Union[Unset, Any]):
            link (Union[List[str], None, Unset]):
            page (Union[None, Unset, int]):
            tag_set (Union[List[str], None, Unset]):
            time_range (Union[List['SearchChunkDataTimeRangeType0Item'], None, Unset]):
            weights (Union[List['SearchChunkDataWeightsType0Item'], None, Unset]):
     """

    content: str
    search_type: str
    cross_encoder: Union[None, Unset, bool] = UNSET
    date_bias: Union[None, Unset, bool] = UNSET
    filters: Union[Unset, Any] = UNSET
    link: Union[List[str], None, Unset] = UNSET
    page: Union[None, Unset, int] = UNSET
    tag_set: Union[List[str], None, Unset] = UNSET
    time_range: Union[List['SearchChunkDataTimeRangeType0Item'], None, Unset] = UNSET
    weights: Union[List['SearchChunkDataWeightsType0Item'], None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.search_chunk_data_weights_type_0_item import SearchChunkDataWeightsType0Item
        from ..models.search_chunk_data_time_range_type_0_item import SearchChunkDataTimeRangeType0Item
        content = self.content

        search_type = self.search_type

        cross_encoder: Union[None, Unset, bool]
        if isinstance(self.cross_encoder, Unset):
            cross_encoder = UNSET
        else:
            cross_encoder = self.cross_encoder

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

        time_range: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.time_range, Unset):
            time_range = UNSET
        elif isinstance(self.time_range, list):
            time_range = []
            for time_range_type_0_item_data in self.time_range:
                time_range_type_0_item = time_range_type_0_item_data.to_dict()
                time_range.append(time_range_type_0_item)




        else:
            time_range = self.time_range

        weights: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.weights, Unset):
            weights = UNSET
        elif isinstance(self.weights, list):
            weights = []
            for weights_type_0_item_data in self.weights:
                weights_type_0_item = weights_type_0_item_data.to_dict()
                weights.append(weights_type_0_item)




        else:
            weights = self.weights


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "content": content,
            "search_type": search_type,
        })
        if cross_encoder is not UNSET:
            field_dict["cross_encoder"] = cross_encoder
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
        if time_range is not UNSET:
            field_dict["time_range"] = time_range
        if weights is not UNSET:
            field_dict["weights"] = weights

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.search_chunk_data_weights_type_0_item import SearchChunkDataWeightsType0Item
        from ..models.search_chunk_data_time_range_type_0_item import SearchChunkDataTimeRangeType0Item
        d = src_dict.copy()
        content = d.pop("content")

        search_type = d.pop("search_type")

        def _parse_cross_encoder(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        cross_encoder = _parse_cross_encoder(d.pop("cross_encoder", UNSET))


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


        def _parse_time_range(data: object) -> Union[List['SearchChunkDataTimeRangeType0Item'], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                time_range_type_0 = []
                _time_range_type_0 = data
                for time_range_type_0_item_data in (_time_range_type_0):
                    time_range_type_0_item = SearchChunkDataTimeRangeType0Item.from_dict(time_range_type_0_item_data)



                    time_range_type_0.append(time_range_type_0_item)

                return time_range_type_0
            except: # noqa: E722
                pass
            return cast(Union[List['SearchChunkDataTimeRangeType0Item'], None, Unset], data)

        time_range = _parse_time_range(d.pop("time_range", UNSET))


        def _parse_weights(data: object) -> Union[List['SearchChunkDataWeightsType0Item'], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                weights_type_0 = []
                _weights_type_0 = data
                for weights_type_0_item_data in (_weights_type_0):
                    weights_type_0_item = SearchChunkDataWeightsType0Item.from_dict(weights_type_0_item_data)



                    weights_type_0.append(weights_type_0_item)

                return weights_type_0
            except: # noqa: E722
                pass
            return cast(Union[List['SearchChunkDataWeightsType0Item'], None, Unset], data)

        weights = _parse_weights(d.pop("weights", UNSET))


        search_chunk_data = cls(
            content=content,
            search_type=search_type,
            cross_encoder=cross_encoder,
            date_bias=date_bias,
            filters=filters,
            link=link,
            page=page,
            tag_set=tag_set,
            time_range=time_range,
            weights=weights,
        )

        search_chunk_data.additional_properties = d
        return search_chunk_data

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
