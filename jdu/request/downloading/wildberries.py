import requests

from requests.adapters import HTTPAdapter

from datetime import datetime

from types import TracebackType
from typing import Optional, Type
from jarvis_db.fill.providers import WildBerriesDataProvider
from ..request_utils import get_parents



class SyncWildBerriesDataProvider(WildBerriesDataProvider):

    @staticmethod
    def get_categories() -> list[str]:
        # TODO think about unused method declaration in inheritors
        return get_parents()

    def __init__(self, api_key: str):
        self.__api_key = api_key
        self.__session = requests.Session()
        self.adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100)
        self.__session.mount('http://', self.adapter)

    def __del__(self):
        self.__session.close()
        self.__session = None

    def get_niches(self, categories : list[str]) -> dict[str, list[str]]:
        result = {}
        for category in categories:
            result[category] = self.get_niches_by_category(category)
        return result

    def get_niches_by_category(self, category: str) -> list[str]:
        response = self.__session.get(
            f'https://suppliers-api.wildberries.ru/api/v1/config/object/byparent?parent={category}',
            headers={'Authorization': self.__api_key}
        )
        response.raise_for_status()
        niches = []
        for niche in response.json()['data']:
            niches.append(niche['name'])
        niches.sort()
        return niches

    def get_product_card_info(self, product_id: int) -> dict[str: any]:

        url = f'https://card.wb.ru/cards/detail?spp=27&regions=64,58,83,4,38,80,33,70,82,86,30,69,22,66,31,40,1,48' \
              f'&pricemarginCoeff=1.0&reg=1&appType=1&emp=0&locale=ru&lang=ru&curr=rub' \
              f'&dest=-1221148,-140294,-1701956,123585768&nm={product_id}'
        request = self.__session.get(url)
        json_code = request.json()
        data_card_json:  dict[str: any] = json_code['data']['products'][0]
        product_cost: int = data_card_json['priceU']
        product_name: str = data_card_json['name']
        card_info_dict = {"cost": product_cost, "name": product_name}
        return card_info_dict

    def get_products_by_niche(self, niche: str, pages: int) -> list[tuple[str, int]]:
        result = []
        for i in range(1, pages + 1):
            uri = 'https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=2,12,7,3,6,21,16' \
                  '&curr=rub&dest=-1221148,-140294,-1751445,-364763&emp=0&lang=ru&locale=ru&pricemarginCoeff=1.0' \
                  f'&query={niche}&resultset=catalog&sort=popular&spp=0&suppressSpellcheck=false&page={i}'
            response = self.__session.get(uri)
            response.raise_for_status()
            json_data = response.json()
            if 'data' not in json_data:
                break
            for product in json_data['data']['products']:
                result.append((product['name'], product['id']))
        return result

    def get_product_price_history(self, product_id: int) -> list[tuple[int, datetime]]:
        result = []
        uri = f'https://wbx-content-v2.wbstatic.net/price-history/{product_id}.json?'
        response = self.__session.get(uri)
        response.raise_for_status()
        if response.status_code != 200:
            return result
        for item in response.json():
            result.append(
                (item['price']['RUB'], datetime.fromtimestamp(item['dt'])))
        return result


