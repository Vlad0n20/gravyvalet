from __future__ import annotations

from dataclasses import dataclass

from addon_service.common.exceptions import (
    ItemNotFound,
    UnexpectedAddonError,
)
from addon_toolkit.interfaces import storage
from addon_toolkit.interfaces.storage import (
    ItemResult,
    ItemSampleResult,
    ItemType,
)


class GoogleDriveStorageImp(storage.StorageAddonHttpRequestorImp):
    """storage on google drive

    see https://developers.google.com/drive/api/reference/rest/v3/
    """

    async def get_external_account_id(self, _: dict[str, str]) -> str:
        return ""

    async def list_root_items(self, page_cursor: str = "") -> storage.ItemSampleResult:
        return await self.list_child_items(
            item_id="root",
            page_cursor=page_cursor,
        )

    async def get_item_info(self, item_id: str) -> storage.ItemResult:
        item_id = item_id or "root"
        async with self.network.GET(f"drive/v3/files/{item_id}") as response:
            if response.http_status == 200:
                json = await response.json_content()
                return File(**json).item_result
            elif response.http_status == 404:
                raise ItemNotFound
            else:
                raise UnexpectedAddonError

    async def list_child_items(
        self,
        item_id: str,
        page_cursor: str = "",
        item_type: storage.ItemType | None = None,
    ) -> storage.ItemSampleResult:
        query = {"q": f"'{item_id}' in parents"}
        if page_cursor:
            query["pageToken"] = page_cursor
        if item_type == ItemType.FOLDER:
            query["q"] += " and mimeType='application/vnd.google-apps.folder'"
        elif item_type == ItemType.FILE:
            query["q"] += " and mimeType!='application/vnd.google-apps.folder'"

        async with self.network.GET("drive/v3/files", query=query) as response:
            return _GoogleDriveResult.from_json(
                await response.json_content()
            ).item_sample_result


###
# module-local helpers
@dataclass(frozen=True, slots=True)
class File:
    kind: str
    mimeType: str
    id: str
    name: str

    @property
    def item_result(self) -> ItemResult:
        return ItemResult(
            item_id=self.id,
            item_name=self.name,
            item_type=(
                ItemType.FOLDER
                if self.mimeType == "application/vnd.google-apps.folder"
                else ItemType.FILE
            ),
        )


@dataclass(frozen=True, slots=True)
class _GoogleDriveResult:
    kind: str
    incomplete_search: bool
    files: list[File]
    nextPageToken: str | None = None

    @classmethod
    def from_json(cls, json: dict) -> _GoogleDriveResult:
        return cls(
            kind=json["kind"],
            incomplete_search=json["incompleteSearch"],
            files=[File(**file) for file in json["files"]],
        )

    @property
    def item_sample_result(self):
        return ItemSampleResult(
            items=[file.item_result for file in self.files],
            total_count=len(self.files),
            next_sample_cursor=self.nextPageToken,
        )
