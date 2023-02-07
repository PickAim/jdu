from abc import ABC, abstractmethod

import aiohttp
import requests
from jorm.market.infrastructure import Category, Niche, Product
from jorm.market.items import ProductHistory
from requests.adapters import HTTPAdapter


class DataProvider(ABC):
    def __init__(self):
        self._session_async = aiohttp.ClientSession()
        self._session = requests.Session()
        adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100)
        self._session.mount('http://', adapter)

    def __del__(self):
        self._session.close()
        self._session_async.close()


class DataProviderWithoutKey(DataProvider):
    def __init__(self):
        super().__init__()


class DataProviderWithKey(DataProvider):
    def __init__(self, api_key: str):
        super().__init__()
        self.__api_key: str = api_key


class WildBerriesDataProviderWithoutKey(DataProviderWithoutKey):

    @abstractmethod
    def get_niches_by_category(self, category: str, pages_num: int = -1) -> list[Niche]:
        # TODO implement request.request_utils.get_object_names for it now
        pass

    @abstractmethod
    def get_products_by_niche(self, niche: str, pages_num: int = -1) -> list[Product]:
        pass

    @abstractmethod
    def get_product_price_history(self, product_id: int) -> ProductHistory:
        # TODO look at request.request_utils.get_page_data
        pass

    @abstractmethod
    def get_categories(self) -> list[Category]:
        pass


class WildBerriesDataProviderWithKey(DataProviderWithKey):
    def get_parents(self) -> list[str]:
        parent_categories: list[str] = []
        response = self._session.get('https://suppliers-api.wildberries.ru/content/v1/object/parent/all',
                                     headers={
                                         'Authorization': self.__api_key})

        json_code = response.json()
        for data in json_code['data']:
            parent_categories.append(data['name'])
        return parent_categories
