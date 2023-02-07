from datetime import datetime

from jorm.market.infrastructure import Niche, Product, HandlerType, Category
from jorm.market.items import ProductHistoryUnit, ProductHistory

from jdu.providers.common import WildBerriesDataProviderWithoutKey, WildBerriesDataProviderWithKey


class WildBerriesDataProviderStandard(WildBerriesDataProviderWithKey):

    def __init__(self, api_key: str):
        super().__init__(api_key)


class WildBerriesDataProviderStatistics(WildBerriesDataProviderWithKey):

    def __init__(self, api_key: str):
        super().__init__(api_key)


class WildBerriesDataProviderAds(WildBerriesDataProviderWithKey):

    def __init__(self, api_key: str):
        super().__init__(api_key)


class WildBerriesDataProviderWithoutKeyImpl(WildBerriesDataProviderWithoutKey):

    def __init__(self):
        super().__init__()

    def get_categories(self) -> list[Category]:
        categories_list: list[Category] = []
        url = f'https://static-basket-01.wb.ru/vol0/data/subject-base.json'
        response = self._session.get(url)
        response.raise_for_status()
        json_data = response.json()
        for data in json_data:
            for category_name in data['name']:
                categories_list.append(Category(category_name, {niche.name: niche for niche
                                                                in self.get_niches_by_category(category_name)}))
        return categories_list

    def get_niches_by_category(self, name_category: str, pages_num: int = -1) -> list[Niche]:
        niche_list: list[Niche] = []
        url = f'https://static-basket-01.wb.ru/vol0/data/subject-base.json'
        response = self._session.get(url)
        response.raise_for_status()
        json_data = response.json()
        for data in json_data:
            if data['name'] == name_category:
                for niche in data['childs']:
                    niche_list.append(Niche(niche['name'], {
                        HandlerType.MARKETPLACE: 0,
                        HandlerType.PARTIAL_CLIENT: 0,
                        HandlerType.CLIENT: 0},
                                            0, self.get_products_by_niche(niche['name'], pages_num)))
                break
        return niche_list

    def get_products_by_niche(self, niche: str, pages_num: int = -1) -> list[Product]:
        result: list[Product] = []
        iterator_pages: int = 1
        while True:
            uri = 'https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=2,12,7,3,6,21,16' \
                  '&curr=rub&dest=-1221148,-140294,-1751445,-364763&emp=0&lang=ru&locale=ru&pricemarginCoeff=1.0' \
                  f'&query={niche}&resultset=catalog&sort=popular&spp=0&suppressSpellcheck=false&page={iterator_pages}'
            response = self._session.get(uri)
            response.raise_for_status()
            json_data = response.json()
            if 'data' in json_data and 'products' in json_data['data']:
                for product in json_data['data']['products']:
                    result.append(Product((product['name']), product['priceU'], product['priceU'], product['id']))
                    if len(json_data['data']['products']) == 1:
                        break
            iterator_pages += 1
            if pages_num != -1 and iterator_pages > pages_num:
                break
        return result

    def get_product_price_history(self, product_id: int) -> ProductHistory:
        result: list[ProductHistoryUnit] = []
        uri = f'https://wbx-content-v2.wbstatic.net/price-history/{product_id}.json?'
        response = self._session.get(uri)
        response.raise_for_status()
        if response.status_code != 200:
            return ProductHistory(result)
        for item in response.json():
            result.append(ProductHistoryUnit(item['price']['RUB'], 0, datetime.fromtimestamp(item['dt'])))
        return ProductHistory(result)
