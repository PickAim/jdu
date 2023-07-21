from abc import ABC, abstractmethod

from jdu.providers.base_data_provider import DataProvider


class DataProviderInitializer(ABC):
    def init_data_provider(self, data_provider_to_init: DataProvider):
        self.additional_data_provider(data_provider_to_init)

    @abstractmethod
    def additional_data_provider(self, data_provider_to_init: DataProvider):
        return
