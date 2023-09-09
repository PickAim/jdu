from jorm.server.providers.initializers import DataProviderInitializer

from jdu.support.commission.wildberries_commission_resolver import (
    WildberriesCommissionResolver,
)
from jdu.support.constant import WILDBERRIES_NAME


class TestWildberriesDataProviderInitializer(DataProviderInitializer):
    def additional_init_data_provider(self, data_provider):
        data_provider.commission_resolver = WildberriesCommissionResolver()

    def get_marketplace_name(self) -> str:
        return WILDBERRIES_NAME
