# import dataclasses
# import functools
# import typing

import boto3

from addon_service.authorized_storage_account.models import AuthorizedStorageAccount
from addon_service.credentials.models import ExternalCredentials

# from addon_toolkit.cursor import OffsetCursor
from addon_toolkit.interfaces import storage


class Boto3Client:
    pass


class S3ClientImp(storage.ClientRequestorImp):
    client: Boto3Client


class S3StorageImp(storage.StorageAddonImp, S3ClientImp):
    """storage on Amazon S3"""

    @classmethod
    def validate_credentials(cls, credentials: ExternalCredentials):
        access_key = credentials.decrypted_credentials.access_key
        secret_key = credentials.decrypted_credentials.secret_key
        s3 = boto3.client(
            "s3", aws_access_key_id=access_key, aws_secret_access_key=secret_key
        )
        response = s3.list_buckets()
        if response:
            return True
        return False

    def construct_client(self, account: AuthorizedStorageAccount):
        access_key = account._credentials.decrypted_credentials.access_key
        secret_key = account._credentials.decrypted_credentials.secret_key
        self.client = boto3.client(
            "s3", aws_access_key_id=access_key, aws_secret_access_key=secret_key
        )

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
