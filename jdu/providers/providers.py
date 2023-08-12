from abc import ABC, abstractmethod
from typing import Type

from jorm.market.infrastructure import Category, Niche, Product, Warehouse
from jorm.market.items import ProductHistory
from jorm.support.types import StorageDict

from jdu.providers.base_data_provider import DataProvider
from jdu.providers.initializers import DataProviderInitializer
from jdu.support.utils import get_request_json


class DataProviderWithoutKey(DataProvider, ABC):
    def __init__(self, data_provider_initializer_class: Type[DataProviderInitializer]):
        super().__init__()
        data_provider_initializer_class().init_object(self)

    @abstractmethod
    def get_products_globals_ids(self, niche: str,
                                 products_count: int = -1) -> list[int]:
        pass

    @abstractmethod
    def get_products(self, niche_name: str,
                     category_name: str,
                     products_global_ids: list[int]) -> list[Product]:
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
    def get_niche(self, niche_name: str) -> Niche:
        pass

    @abstractmethod
    def get_top_request_by_marketplace_query(self, search_period: str = 'month', number_top: int = 1000,
                                             search_query: str = '') -> dict[str, int] | None:
        pass

    @abstractmethod
    def get_category_and_niche(self, product_id: int) -> tuple[str, str] | None:
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


class DataProviderWithKey(DataProvider, ABC):
    def __init__(self, api_key: str, data_provider_initializer_class: Type[DataProviderInitializer]):
        super().__init__()
        self._api_key: str = api_key
        data_provider_initializer_class().init_object(self)

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
    def get_user_products(self) -> list[int]:
        pass

    @abstractmethod
    def get_nearest_keywords(self, word: str) -> list[str]:
        pass
