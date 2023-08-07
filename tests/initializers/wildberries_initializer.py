from jdu.db_tools.fill.initializers import DBFillerInitializer
from jdu.providers.initializers import DataProviderInitializer
from jdu.support.commission.wildberries_commission_resolver import WildberriesCommissionResolver


class WildberriesTestDataProviderInitializer(DataProviderInitializer):
    WILDBERRIES_NAME = 'wildberries'

    def additional_init_data_provider(self, data_provider):
        data_provider.commission_resolver = WildberriesCommissionResolver()

    def get_marketplace_name(self) -> str:
        return self.WILDBERRIES_NAME


class WildberriesTestDBFillerInitializer(DBFillerInitializer):
    WILDBERRIES_NAME = 'wildberries'

    def get_marketplace_name(self) -> str:
        return self.WILDBERRIES_NAME
