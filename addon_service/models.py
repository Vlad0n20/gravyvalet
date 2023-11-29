""" Import models here so they auto-detect for makemigrations """
from addon_service.authorized_storage_account.models import AuthorizedStorageAccount
from addon_service.configured_storage_addon.models import ConfiguredStorageAddon
from addon_service.external_account.models import ExternalAccount
from addon_service.external_credentials.models import ExternalCredentials
from addon_service.external_service.models import ExternalService
from addon_service.external_storage_service.models import ExternalStorageService
from addon_service.internal_resource.models import InternalResource
from addon_service.internal_user.models import InternalUser


__all__ = (
    "AuthorizedStorageAccount",
    # 'AuthorizedComputeAccount',
    "ConfiguredStorageAddon",
    # 'ConfiguredComputeAddon',
    "ExternalAccount",
    "ExternalCredentials",
    "ExternalService",
    "ExternalStorageService",
    # 'ExternalComputeService',
    "InternalResource",
    "InternalUser",
)
