import asyncio
from asyncio import Task, AbstractEventLoop
from datetime import datetime

import aiohttp
from aiohttp import ClientSession
from jorm.market.infrastructure import Niche, Product, HandlerType, Category
from jorm.market.items import ProductHistoryUnit, ProductHistory
from requests import Response

from jdu.providers.common import WildBerriesDataProviderWithoutKey, WildBerriesDataProviderWithKey
from jdu.services.sorters import score_object_names, sort_by_len_alphabet


class WildBerriesDataProviderStandard(WildBerriesDataProviderWithKey):

    def __init__(self, api_key: str):
        super().__init__(api_key)

    def get_nearest_names(self, text: str) -> list[str]:
        object_name_list: list[str] = []
        response: Response = self._session.get('https://suppliers-api.wildberries.ru/content/v1/object/all?name=' + text
                                               + '&top=100',
                                               headers={
                                                   'Authorization': self.__api_key})
        json_code: any = response.json()
        for data in json_code['data']:
            object_name_list.append(data['objectName'])
        return object_name_list

    def get_nearest_keywords(self, word: str) -> list[str]:
        names: list[str] = self.get_nearest_names(word)
        scored_dict: dict[float, list[str]] = score_object_names(word, names)
        result: list[str] = []
        for score in scored_dict.keys():
            result.extend(sort_by_len_alphabet(scored_dict[score]))
        return result


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
        url: str = f'https://static-basket-01.wb.ru/vol0/data/subject-base.json'
        response: Response = self._session.get(url)
        response.raise_for_status()
        json_data: any = response.json()
        for data in json_data:
            for category_name in data['name']:
                categories_list.append(Category(category_name, {niche.name: niche for niche
                                                                in self.get_niches_by_category(category_name)}))
        return categories_list

    def get_niches_by_category(self, name_category: str, niche_num: int = -1, pages_num: int = -1, ) -> list[Niche]:
        niche_list: list[Niche] = []
        iterator_niche = 1
        url: str = f'https://static-basket-01.wb.ru/vol0/data/subject-base.json'
        response: Response = self._session.get(url)
        response.raise_for_status()
        json_data: any = response.json()
        for data in json_data:
            if data['name'] == name_category:
                for niche in data['childs']:
                    niche_list.append(Niche(niche['name'], {
                        HandlerType.MARKETPLACE: 0,
                        HandlerType.PARTIAL_CLIENT: 0,
                        HandlerType.CLIENT: 0},
                                            0, self.get_products_by_niche(niche['name'], pages_num)))
                    iterator_niche += 1
                    if iterator_niche != -1 and iterator_niche > niche_num:
                        break
                break
        return niche_list

    async def load_all_product_niche(self, niche: str, pages_num: int) -> list[Product]:
        result: list[Product] = []
        iterator_page: int = 1
        name_id_cost_list: list[tuple[str, int, int]] = []
        while True:
            url: str = f'https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=2,12,7,3,6,21,16' \
                       f'&curr=rub&dest=-1221148,-140294,-1751445,-364763&emp=0' \
                       f'&lang=ru&locale=ru&pricemarginCoeff=1.0' \
                       f'&query={niche}&resultset=catalog' \
                       f'&sort=popular&spp=0&suppressSpellcheck=false&page={iterator_page}'
            request: Response = self._session.get(
                url
            )
            json_code: any = request.json()
            if 'data' not in json_code:
                break
            for product in json_code['data']['products']:
                name_id_cost_list.append(
                    (product['name'], product['id'], product['priceU']))
            iterator_page += 1
            if pages_num != -1 and iterator_page > pages_num:
                break
        async with aiohttp.ClientSession() as clientSession:
            tasks: list[Task] = []
            for name_id_cost in name_id_cost_list:
                task = asyncio.create_task(self.get_product_price_history(clientSession, name_id_cost[1]))
                tasks.append(task)
            product_price_history_list: any = await asyncio.gather(*tasks)
            for index in range(len(name_id_cost_list)):
                result.append(Product(name_id_cost_list[index][0],
                                      name_id_cost_list[index][2],
                                      name_id_cost_list[index][1],
                                      product_price_history_list[index], width=0, height=0, depth=0))
        await clientSession.close()
        return result

    def get_products_by_niche(self, niche: str, pages_num: int = -1) -> list[Product]:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        loop: AbstractEventLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result: list[Product] = loop.run_until_complete(self.load_all_product_niche(niche, pages_num))
        loop.close()
        return result

    async def get_product_price_history(self, session: ClientSession, product_id: int) -> ProductHistory:
        result: list[ProductHistoryUnit] = []
        url: str = f'https://wbx-content-v2.wbstatic.net/price-history/{product_id}.json?'
        async with session.get(url=url) as request:
            response_status: int = request.status
            if response_status != 200:
                return ProductHistory()
            else:
                json_code = await request.json()
                for item in json_code:
                    result.append(ProductHistoryUnit(item['price']['RUB'], 0, datetime.fromtimestamp(item['dt'])))
            return ProductHistory(result)

    def get_storage_dict(self, product_id: int) -> dict[int, int]:
        url = f'https://card.wb.ru/cards/detail?spp=27&regions=64,58,83,4,38,80,33,70,82,86,30,69,22,66,31,40,1,48' \
              f'&pricemarginCoeff=1.0&reg=1&appType=1&emp=0&locale=ru&lang=ru&curr=rub' \
              f'&dest=-1221148,-140294,-1701956,123585768&nm={product_id}'
        request = self._session.get(url)
        json_code = request.json()
        product_sizes = json_code['data']['products'][0]['sizes']
        stocks: list[any] = []
        for data in product_sizes:
            stocks.extend(data['stocks'])
        warehouse_leftover_dict = {}
        for data_storage in stocks:
            warehouse_leftover_dict[data_storage['wh']] = data_storage['qty']
        return warehouse_leftover_dict

    def get_storage_data(self, product_ids: list[int]) -> dict[int, dict[int, int]]:
        main_dict: dict[int, dict[int, int]] = {}
        for product_id in product_ids:
            dicts = self.get_storage_dict(product_id)
            main_dict[product_id] = dicts
        return main_dict
