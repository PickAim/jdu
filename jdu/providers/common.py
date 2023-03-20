from abc import ABC, abstractmethod

import requests
from aiohttp import ClientSession
from jorm.market.infrastructure import Category, Niche, Product
from jorm.market.items import ProductHistory
from jorm.support.types import StorageDict
from requests.adapters import HTTPAdapter


class DataProvider(ABC):
    def __init__(self):
        self._session = requests.Session()
        __adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100)
        self._session.mount('http://', __adapter)

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
    def get_niches_by_category(self, category: str, niche_num: int = -1) -> list[Niche]:
        pass

    @abstractmethod
    def get_products_by_niche(self, niche: str, pages_num: int = -1, count_products: int = -1) -> list[Product]:
        pass

    @abstractmethod
    def get_product_price_history(self, session: ClientSession, product_id: int) -> ProductHistory:
        pass

    @abstractmethod
    def get_categories(self, category_num: int = -1) -> list[Category]:
        pass

    @abstractmethod
    def get_storage_dict(self, product_id: int) -> StorageDict:
        pass

    @abstractmethod
    def get_storage_data(self, product_ids: list[int]) -> dict[int: StorageDict]:
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
