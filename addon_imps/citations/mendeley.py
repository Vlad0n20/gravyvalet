import asyncio

from addon_toolkit.interfaces.citation import (
    CitationAddonImp,
    ItemResult,
    ItemSampleResult,
    ItemType,
)


class MendeleyCitationImp(CitationAddonImp):
    async def get_external_account_id(self, auth_result_extras: dict[str, str]) -> str:
        async with self.network.GET(
            "profiles/me",
        ) as response:
            profile_info = await response.json_content()
            user_id = profile_info.get("id")
            if not user_id:
                raise KeyError("Failed to fetch user ID from Mendeley.")
            return str(user_id)

    async def list_root_collections(self) -> ItemSampleResult:
        async with self.network.GET("folders") as response:
            response_json = await response.json_content()
            return self._parse_collection_response(response_json)

    async def list_collection_items(
        self,
        collection_id: str,
        filter_items: ItemType | None = None,
    ) -> ItemSampleResult:
        async with self.network.GET(
            f"folders/{collection_id}/documents",
        ) as response:
            import pydevd_pycharm

            pydevd_pycharm.settrace(
                "host.docker.internal",
                port=12346,
                stdoutToServer=True,
                stderrToServer=True,
            )
            document_ids = await response.json_content()

            items = await self._fetch_documents_details(document_ids, filter_items)

            return ItemSampleResult(items=items, total_count=len(items))

    async def _fetch_documents_details(
        self, document_ids: list[dict], filter_items: ItemType | None
    ) -> list[ItemResult]:
        items = []

        async def fetch_item_details(item_id):
            async with self.network.GET(f"documents/{item_id}") as item_response:
                item_details = await item_response.json_content()
                item_name = item_details.get("title", f"Untitled Document {item_id}")
                item_type = item_details.get("type", "unknown")

                if filter_items is None or filter_items == item_type:
                    items.append(
                        ItemResult(
                            item_id=item_id,
                            item_name=item_name,
                            item_type=item_type,
                            item_path=None,
                            csl=item_details.get("csl", {}),
                        )
                    )

        tasks = [fetch_item_details(doc["id"]) for doc in document_ids]
        await asyncio.gather(*tasks)

        return items

    def _parse_collection_response(self, response_json: dict) -> ItemSampleResult:
        print(response_json, flush=True)
        items = [
            ItemResult(
                item_id=collection["id"],
                item_name=collection["name"],
                item_type="COLLECTION",
                item_path=None,
                csl=None,
            )
            for collection in response_json
        ]

        return ItemSampleResult(items=items, total_count=len(items))