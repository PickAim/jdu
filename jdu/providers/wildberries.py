import requests

from requests.adapters import HTTPAdapter

from datetime import datetime

from jdu.providers.common import WildBerriesDataProvider
from jdu.request.request_utils import get_parents
from jorm.market.infrastructure import Category, Niche, Product, HandlerType
from jorm.market.items import ProductHistoryUnit, ProductHistory


class SyncWildBerriesDataProvider(WildBerriesDataProvider):

    def __init__(self, api_key: str):
        self.__api_key = api_key
        self.__session = requests.Session()
        self.adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100)
        self.__session.mount('http://', self.adapter)

    def __del__(self):
        self.__session.close()
        self.__session = None

    def get_categories(self) -> list[Category]:
        category_list: list[str] = get_parents()
        result: list[Category] = []
        for category in category_list:
            result.append(Category(category, {category: self.get_niches_by_category(category)}))
        return result

    def get_niches_by_category(self, name_category: str) -> list[Niche]:
        niche_list: list[Niche] = []
        url = f'https://static-basket-01.wb.ru/vol0/data/subject-base.json'
        response = self.__session.get(url)
        response.raise_for_status()
        json_data = response.json()
        for data in json_data:
            if data['name'] == name_category:
                for niche in data['childs']:
                    niche_list.append(Niche(niche['name'], {
                                                            HandlerType.MARKETPLACE: 0,
                                                            HandlerType.PARTIAL_CLIENT: 0,
                                                            HandlerType.CLIENT: 0},
                                                            0, self.get_products_by_niche(niche['name'])))
                break
        return niche_list

    def get_products_by_niche(self, niche: str) -> list[Product]:
        result: list[Product] = []
        iterator_pages: int = 1
        while True:
            uri = 'https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=2,12,7,3,6,21,16' \
                  '&curr=rub&dest=-1221148,-140294,-1751445,-364763&emp=0&lang=ru&locale=ru&pricemarginCoeff=1.0' \
                  f'&query={niche}&resultset=catalog&sort=popular&spp=0&suppressSpellcheck=false&page={iterator_pages}'
            response = self.__session.get(uri)
            response.raise_for_status()
            json_data = response.json()
            if 'data' not in json_data:
                break
            for product in json_data['data']['products']:
                if len(json_data['data']['products']) == 1:
                    result.append(Product((product['name']), product['priceU'], product['priceU'], product['id']))
                    break
                result.append(Product((product['name']), product['priceU'], product['priceU'], product['id']))
            iterator_pages += 1
        return result

    def get_product_price_history(self, product_id: int) -> ProductHistory:
        result: list[ProductHistoryUnit] = []
        uri = f'https://wbx-content-v2.wbstatic.net/price-history/{product_id}.json?'
        response = self.__session.get(uri)
        response.raise_for_status()
        if response.status_code != 200:
            return ProductHistory(result)
        for item in response.json():
            result.append(ProductHistoryUnit(item['price']['RUB'], 0, datetime.fromtimestamp(item['dt'])))
        return ProductHistory(result)
