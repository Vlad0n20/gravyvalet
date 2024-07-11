# import dataclasses
# import functools
# import typing

from addon_service.credentials.models import ExternalCredentials

# from addon_toolkit.cursor import OffsetCursor
from addon_toolkit.interfaces import storage


class S3StorageImp(storage.StorageAddonImp):
    """storage on Amazon S3"""

    @classmethod
    def validate_access_key_secret_key(cls, credentials: ExternalCredentials):
        return

    async def get_item_info(self, item_id: str) -> storage.ItemResult:
        return

    async def list_root_items(self, page_cursor: str = "") -> storage.ItemSampleResult:
        return

    async def list_child_items(
        self,
        item_id: str,
        page_cursor: str = "",
        item_type: storage.ItemType | None = None,
    ) -> storage.ItemSampleResult:
        return
