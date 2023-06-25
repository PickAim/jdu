from abc import ABC, abstractmethod

import requests
from jorm.market.infrastructure import Category, Niche, Product, Warehouse
from jorm.market.items import ProductHistory
from jorm.support.types import StorageDict
from requests.adapters import HTTPAdapter, Response


class DataProvider(ABC):
    THREAD_TASK_COUNT = 100

    def __init__(self):
        self._session = requests.Session()
        __adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100)
        self._session.mount('https://', __adapter)

    def get_exchange_rate(self, currency: str):
        url: str = 'https://www.cbr-xml-daily.ru/daily_json.js'
        response: Response = self._session.get(url)
        response.raise_for_status()
        json_data = response.json()
        return json_data['Valute'][currency]

    def __del__(self):
        self._session.close()


class DataProviderWithoutKey(DataProvider):
    def __init__(self):
        super().__init__()


class DataProviderWithKey(DataProvider):
    def __init__(self, api_key: str):
        super().__init__()
        self._api_key: str = api_key


class WildBerriesDataProviderWithoutKey(DataProviderWithoutKey):
    def __init__(self):
        super().__init__()
        self.marketplace_name = 'wildberries'

    @abstractmethod
    def get_products_id_to_name_cost_dict(self, niche: str,
                                          products_count: int = -1) -> dict[int, tuple[str, int]]:
        pass

    @abstractmethod
    def get_products(self, niche_name: str, category_name: str, id_to_name_cost_dict: list[tuple[int, str, int]]) -> \
            list[Product]:
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


class WildBerriesDataProviderWithKey(DataProviderWithKey):
    def get_parents(self) -> list[str]:
        parent_categories: list[str] = []
        response = self._session.get('https://suppliers-api.wildberries.ru/content/v1/object/parent/all',
                                     headers={
                                         'Authorization': self._api_key})

        json_code = response.json()
        for data in json_code['data']:
            parent_categories.append(data['name'])
        return parent_categories

    @abstractmethod
    def get_warehouse(self) -> list[Warehouse]:
        pass
