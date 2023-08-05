import requests
from requests.adapters import HTTPAdapter

from jdu.db_tools.fill.initializers import DBFillerInitializer
from jdu.providers.initializers import DataProviderInitializer
from jdu.support.commission.wildberries_commission_resolver import WildberriesCommissionResolver


class WildberriesTestDataProviderInitializer(DataProviderInitializer):
    WILDBERRIES_NAME = 'wildberries'

    def additional_init_data_provider(self, data_provider):
        data_provider.commission_resolver = WildberriesCommissionResolver()
        data_provider.session = requests.Session()
        __adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100)
        data_provider.session.mount('https://', __adapter)

    def get_marketplace_name(self) -> str:
        return self.WILDBERRIES_NAME


class WildberriesTestDBFillerInitializer(DBFillerInitializer):
    WILDBERRIES_NAME = 'wildberries'

    def get_marketplace_name(self) -> str:
        return self.WILDBERRIES_NAME
