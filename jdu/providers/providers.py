from abc import ABC, abstractmethod

import requests
from aiohttp import ClientSession
from jorm.market.infrastructure import Category, Niche, Product, Warehouse
from jorm.market.items import ProductHistory
from jorm.support.types import StorageDict
from requests.adapters import HTTPAdapter

from jdu.support.types import ProductInfo
from jdu.support.utils import get_request_json, get_async_request_json


class DataProvider(ABC):
    THREAD_TASK_COUNT = 100

    def __init__(self):
        self._session = requests.Session()
        __adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100)
        self._session.mount('https://', __adapter)

    def get_request_json(self, url: str):
        return get_request_json(url, self._session)

    @staticmethod
    async def get_async_request_json(url: str, client_session: ClientSession):
        return await get_async_request_json(url, client_session)

    def get_exchange_rate(self, currency: str):
        url: str = 'https://www.cbr-xml-daily.ru/daily_json.js'
        json_data = self.get_request_json(url)
        return json_data['Valute'][currency]

    def __del__(self):
        self._session.close()


class DataProviderWithoutKey(DataProvider):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_products_mapped_info(self, niche: str,
                                 products_count: int = -1) -> list[ProductInfo]:
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


class DataProviderWithKey(DataProvider):
    def __init__(self, api_key: str):
        super().__init__()
        self._api_key: str = api_key

    def get_authorized_request_json(self, url: str):
        headers = {
            'Authorization': self._api_key
        }
        return get_request_json(url, self._session, headers)


class UserMarketDataProvider(DataProviderWithKey, ABC):
    def __init__(self, api_key: str):
        super().__init__(api_key)

    @abstractmethod
    def get_warehouses(self) -> list[Warehouse]:
        pass

    @abstractmethod
    def get_nearest_keywords(self, word: str) -> list[str]:
        pass
