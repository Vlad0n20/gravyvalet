from addon_service.common.aiohttp_session import get_singleton_client_session__blocking
from addon_service.common.network import GravyvaletHttpRequestor
from addon_service.models import AuthorizedStorageAccount
from addon_toolkit.interfaces.storage import (
    ClientRequestorImp,
    StorageAddonImp,
    StorageConfig,
)


def get_storage_addon_instance(
    imp_cls: type[StorageAddonImp],
    account: AuthorizedStorageAccount,
    config: StorageConfig,
) -> StorageAddonImp:
    assert issubclass(imp_cls, StorageAddonImp)
    imp = imp_cls(
        config=config,
        network=GravyvaletHttpRequestor(
            client_session=get_singleton_client_session__blocking(),
            prefix_url=config.external_api_url,
            account=account,
        ),
    )
    if isinstance(imp, ClientRequestorImp):
        imp.construct_client(account)

    return imp
