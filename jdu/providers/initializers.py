from abc import abstractmethod
from typing import final

import requests
from jorm.jarvis.initialization import Initializer
from requests.adapters import HTTPAdapter

from jdu.providers.base_data_provider import DataProvider


class DataProviderInitializer(Initializer):
    def __init__(self):
        super().__init__()

    def init_object(self, initializable_object: DataProvider) -> None:
        super().init_object(initializable_object)

    @final
    def _init_something(self, initializable_object: DataProvider) -> None:
        initializable_object.marketplace_name = self.get_marketplace_name()
        initializable_object.session = requests.Session()
        __adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100)
        initializable_object.session.mount('https://', __adapter)
        self.additional_init_data_provider(initializable_object)

    @abstractmethod
    def additional_init_data_provider(self, data_provider_to_init: DataProvider):
        return

    @abstractmethod
    def get_marketplace_name(self) -> str:
        return 'default'
