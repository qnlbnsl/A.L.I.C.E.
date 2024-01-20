from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.file_upload_completed_notification_with_name import FileUploadCompletedNotificationWithName


T = TypeVar("T", bound="NotificationReturn")


@_attrs_define
class NotificationReturn:
    """
    Attributes:
        full_count (int):
        notifications (List['FileUploadCompletedNotificationWithName']):
        total_pages (int):
    """

    full_count: int
    notifications: List["FileUploadCompletedNotificationWithName"]
    total_pages: int
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        full_count = self.full_count

        notifications = []
        for notifications_item_data in self.notifications:
            notifications_item = notifications_item_data.to_dict()
            notifications.append(notifications_item)

        total_pages = self.total_pages

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "full_count": full_count,
                "notifications": notifications,
                "total_pages": total_pages,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.file_upload_completed_notification_with_name import FileUploadCompletedNotificationWithName

        d = src_dict.copy()
        full_count = d.pop("full_count")

        notifications = []
        _notifications = d.pop("notifications")
        for notifications_item_data in _notifications:
            notifications_item = FileUploadCompletedNotificationWithName.from_dict(notifications_item_data)

            notifications.append(notifications_item)

        total_pages = d.pop("total_pages")

        notification_return = cls(
            full_count=full_count,
            notifications=notifications,
            total_pages=total_pages,
        )

        notification_return.additional_properties = d
        return notification_return

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
