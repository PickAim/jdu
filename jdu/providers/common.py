from abc import ABC, abstractmethod

import requests
from jorm.market.infrastructure import Category, Niche, Product
from jorm.market.items import ProductHistory
from jorm.support.types import StorageDict
from requests.adapters import HTTPAdapter, Response


class DataProvider(ABC):
    def __init__(self):
        self._session = requests.Session()
        __adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100)
        self._session.mount('http://', __adapter)

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
    def get_product_name_id_cost_list(self, niche: str, pages_num: int, products_count: int) -> list[
        tuple[str, int, int]]:
        pass

    @abstractmethod
    def get_products(self, niche: str, pages_num: int = -1, products_count: int = -1) -> list[Product]:
        pass

    @abstractmethod
    def get_price_history(self, product_id: int) -> ProductHistory:
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

    @abstractmethod
    def get_categories(self, category_names_list: list[str]) -> list[Category]:
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
