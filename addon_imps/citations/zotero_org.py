from addon_toolkit.interfaces.citation import (
    CitationAddonImp,
    ItemResult,
    ItemSampleResult,
    ItemType,
)


class ZoteroOrgCitationImp(CitationAddonImp):

    async def get_external_account_id(self, auth_result_extras: dict[str, str]) -> str:
        user_id = auth_result_extras.get("userID")
        if user_id:
            return user_id
        async with self.network.GET(
            "keys",
        ) as response:
            if response.status == 200:
                key_info = await response.json_content()
                user_id = key_info.get("userID")
                if not user_id:
                    raise KeyError("Failed to fetch user ID from Zotero.")
                return str(user_id)
            else:
                raise ValueError(
                    f"Failed to fetch key information. Status code: {response.status}"
                )

    async def list_root_collections(self) -> ItemSampleResult:
        async with self.network.GET(
            f"users/{self.config.external_account_id}/collections"
        ) as response:
            collections = await response.json_content()
            items = [
                ItemResult(
                    item_id=col["key"],
                    item_name=col["data"].get("name", "Unnamed Collection"),
                    item_type=ItemType.COLLECTION,
                )
                for col in collections
            ]
            return ItemSampleResult(items=items, total_count=len(items))

    async def list_collection_items(
        self,
        collection_id: str,
        filter_items: ItemType | None = None,
    ) -> ItemSampleResult:
        async with self.network.GET(
            f"users/{self.config.external_account_id}/collections/{collection_id}/items",
        ) as response:
            items_json = await response.json_content()
            items = [
                ItemResult(
                    item_id=item["key"],
                    item_name=item["data"].get("title", "Unnamed title"),
                    item_type=ItemType.DOCUMENT,
                )
                for item in items_json
                if filter_items is None
            ]
            return ItemSampleResult(items=items, total_count=len(items))
