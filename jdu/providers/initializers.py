from abc import ABC, abstractmethod

from jdu.providers.base_data_provider import DataProvider


class DataProviderInitializer(ABC):
    def init_data_provider(self, data_provider_to_init: DataProvider):
        data_provider_to_init.marketplace_name = self.get_marketplace_name()
        self.additional_init_data_provider(data_provider_to_init)

    @abstractmethod
    def additional_init_data_provider(self, data_provider_to_init: DataProvider):
        return

    @abstractmethod
    def get_marketplace_name(self) -> str:
        return 'default'
