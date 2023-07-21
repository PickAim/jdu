from abc import ABC, abstractmethod
from typing import Type

from jorm.market.infrastructure import Category, Niche, Product, Warehouse
from jorm.market.items import ProductHistory
from jorm.support.types import StorageDict

from jdu.providers.base_data_provider import DataProvider
from jdu.providers.initializers_provider import DataProviderInitializer
from jdu.support.types import ProductInfo
from jdu.support.utils import get_request_json


class __InitializableDataProvider(DataProvider):
    def __init__(self, data_provider_initializer_class: Type[DataProviderInitializer]):
        super().__init__()
        data_provider_initializer_class().init_data_provider(self)


class DataProviderWithoutKey(__InitializableDataProvider, ABC):
    def __init__(self, data_provider_initializer_class: Type[DataProviderInitializer]):
        super().__init__(data_provider_initializer_class)

    @abstractmethod
    def get_products_mapped_info(self, niche: str,
                                 products_count: int = -1) -> set[ProductInfo]:
        pass

    @abstractmethod
    def get_products(self, niche_name: str, category_name: str,
                     id_to_name_cost_dict: list[ProductInfo]) -> list[Product]:
        pass

    @abstractmethod
    def get_product_price_history(self, product_id: int) -> ProductHistory:
        pass

    @abstractmethod
    def get_niches_names(self, category: str, niche_num: int = -1) -> list[str]:
        pass

    @abstractmethod
    def get_niches(self, niche_names_list: list[str]) -> list[Niche]:
        pass

    @abstractmethod
    def get_categories_names(self, category_num: int = -1) -> list[str]:
        pass

    @staticmethod
    @abstractmethod
    def get_categories(category_names_list: list[str]) -> list[Category]:
        pass

    @abstractmethod
    def get_storage_dict(self, product_id: int) -> StorageDict:
        pass


class DataProviderWithKey(__InitializableDataProvider, ABC):
    def __init__(self, api_key: str, data_provider_initializer_class: Type[DataProviderInitializer]):
        super().__init__(data_provider_initializer_class)
        self._api_key: str = api_key

    def get_authorized_request_json(self, url: str):
        headers = {
            'Authorization': self._api_key
        }
        return get_request_json(url, self.session, headers)


class UserMarketDataProvider(DataProviderWithKey, ABC):
    def __init__(self, api_key: str, data_provider_initializer_class: Type[DataProviderInitializer]):
        super().__init__(api_key, data_provider_initializer_class)

    @abstractmethod
    def get_warehouses(self) -> list[Warehouse]:
        pass

    @abstractmethod
    def get_nearest_keywords(self, word: str) -> list[str]:
        pass
