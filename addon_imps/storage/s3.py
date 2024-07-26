# import dataclasses
# import functools
# import typing
import boto3
from asgiref.sync import sync_to_async
from botocore import exceptions
from django.core.exceptions import ValidationError

# from addon_toolkit.cursor import OffsetCursor
from addon_toolkit.interfaces import storage


# from addon_service.authorized_storage_account.models import AuthorizedStorageAccount
# from addon_service.credentials.models import ExternalCredentials


class Boto3Client:
    pass


class S3ClientImp(storage.ClientRequestorImp):
    client: Boto3Client


class S3StorageImp(storage.StorageAddonImp, S3ClientImp):
    """storage on Amazon S3"""

    @classmethod
    def validate_credentials(cls, credentials):
        access_key = credentials.access_key
        secret_key = credentials.secret_key
        s3 = boto3.client(
            "s3", aws_access_key_id=access_key, aws_secret_access_key=secret_key
        )
        try:
            s3.list_buckets()
        except exceptions.ClientError:
            raise ValidationError("Fail to validate access key and secret key")

    @sync_to_async
    def construct_client(self, account):
        access_key = account._credentials.decrypted_credentials.access_key
        secret_key = account._credentials.decrypted_credentials.secret_key
        self.client = boto3.client(
            "s3", aws_access_key_id=access_key, aws_secret_access_key=secret_key
        )

    async def get_item_info(self, item_id: str) -> storage.ItemResult:
        bucket = item_id.split("/", 1)[0]
        key = item_id.split("/", 1)[1]
        response = self.client.list_objects(Bucket=bucket, Prefix=key, Delimiter="/")
        if response["Contents"]:
            if len(response["Contents"]) == 1 and ("CommonPrefixes" not in response):
                # that means this is a file, not a folder
                return storage.ItemResult(
                    item_id=response["Contents"][0]["Key"],
                    item_name=response["Contents"][0]["Key"],
                    item_type=storage.ItemType.FILE,
                )
            else:
                # That means this is a folder
                return storage.ItemResult(
                    item_id=item_id,
                    item_name=item_id,
                    item_type=storage.ItemType.FOLDER,
                )
        return None

    async def list_root_items(self, page_cursor: str = "") -> storage.ItemSampleResult:
        results = list(self.list_buckets())
        return storage.ItemSampleResult(
            items=results,
            total_count=len(results),
        )

    async def list_child_items(
        self,
        item_id: str,
        page_cursor: str = "",
        item_type: storage.ItemType | None = None,
    ) -> storage.ItemSampleResult:
        bucket = item_id.split("/", 1)[0]
        key = item_id.split("/", 1)[1]
        response = self.client.list_objects(Bucket=bucket, Prefix=key, Delimiter="/")
        results = []
        if response["CommonPrefixes"]:
            for folder in response["CommonsPrefixes"]:
                results.append(
                    storage.ItemResult(
                        item_id=folder["Prefix"],
                        item_name=folder["Prefix"],
                        item_type=storage.ItemType.FOLDER,
                    )
                )
        if response["Contents"]:
            for file in response["Contents"]:
                results.append(
                    storage.ItemResult(
                        item_id=file["Key"],
                        item_name=bucket["Key"],
                        item_type=storage.ItemType.FILE,
                    )
                )
        return

    def list_buckets(self):
        for bucket in self.client.list_buckets()["Buckets"]:
            yield storage.ItemResult(
                item_id=bucket["Name"],
                item_name=bucket["Name"],
                item_type=storage.ItemType.FOLDER,
            )
