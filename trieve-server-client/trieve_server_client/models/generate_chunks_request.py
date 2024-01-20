from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast, List
from typing import cast
from typing import Dict

if TYPE_CHECKING:
  from ..models.chat_message_proxy import ChatMessageProxy





T = TypeVar("T", bound="GenerateChunksRequest")


@_attrs_define
class GenerateChunksRequest:
    """ 
        Attributes:
            chunk_ids (List[str]):
            prev_messages (List['ChatMessageProxy']):
     """

    chunk_ids: List[str]
    prev_messages: List['ChatMessageProxy']
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.chat_message_proxy import ChatMessageProxy
        chunk_ids = self.chunk_ids





        prev_messages = []
        for prev_messages_item_data in self.prev_messages:
            prev_messages_item = prev_messages_item_data.to_dict()
            prev_messages.append(prev_messages_item)






        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "chunk_ids": chunk_ids,
            "prev_messages": prev_messages,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.chat_message_proxy import ChatMessageProxy
        d = src_dict.copy()
        chunk_ids = cast(List[str], d.pop("chunk_ids"))


        prev_messages = []
        _prev_messages = d.pop("prev_messages")
        for prev_messages_item_data in (_prev_messages):
            prev_messages_item = ChatMessageProxy.from_dict(prev_messages_item_data)



            prev_messages.append(prev_messages_item)


        generate_chunks_request = cls(
            chunk_ids=chunk_ids,
            prev_messages=prev_messages,
        )

        generate_chunks_request.additional_properties = d
        return generate_chunks_request

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
