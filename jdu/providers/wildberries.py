import asyncio
from asyncio import Task, AbstractEventLoop
from datetime import datetime

import aiohttp
from aiohttp import ClientSession
from jorm.market.infrastructure import Niche, Product, HandlerType, Category
from jorm.market.items import ProductHistoryUnit, ProductHistory
from jorm.support.types import StorageDict, SpecifiedLeftover
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
                                                   'Authorization': self._api_key})
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

    def get_categories(self, category_num=-1) -> list[Category]:
        categories_list: list[Category] = []
        url: str = f'https://static-basket-01.wb.ru/vol0/data/subject-base.json'
        response: Response = self._session.get(url)
        response.raise_for_status()
        json_data: any = response.json()
        iterator_category: int = 1
        for data in json_data:
            categories_list.append(Category(data['name']))
            iterator_category += 1
            if category_num != -1 and iterator_category > category_num:
                break
        return categories_list

    def get_niches_by_category(self, name_category: str, niche_num: int = -1) -> list[Niche]:
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
                        HandlerType.CLIENT: 0}, 0))
                    iterator_niche += 1
                    if niche_num != -1 and iterator_niche > niche_num:
                        break
                break
        return niche_list

    async def load_all_product_niche(self, niche: str, pages_num: int, count_products: int) -> list[Product]:
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
            if request.status_code != 200:
                break
            json_code: any = request.json()
            if 'data' not in json_code:
                break
            iterator_product: int = 0
            for product in json_code['data']['products']:
                if count_products != -1 and iterator_product > count_products:
                    break
                name_id_cost_list.append(
                    (product['name'], product['id'], product['priceU']))
                iterator_product += 1
            iterator_page += 1
            if pages_num != -1 and iterator_page > pages_num:
                break
        connector = aiohttp.TCPConnector(limit=10)
        async with aiohttp.ClientSession(connector=connector) as clientSession:
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

    def get_products_by_niche(self, niche: str, pages_num: int = -1, count_products: int = -1) -> list[Product]:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        loop: AbstractEventLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result: list[Product] = loop.run_until_complete(self.load_all_product_niche(niche, pages_num, count_products))
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
                    if 'price' not in item or 'RUB' not in item['price'] or 'dt' not in item:
                        continue
                    result.append(ProductHistoryUnit(item['price']['RUB'],
                                                     datetime.fromtimestamp(item['dt']),
                                                     StorageDict()))
                if len(result) > 0:
                    last_item = result[len(result) - 1]
                    last_item.leftover = self.get_storage_dict(product_id)
        return ProductHistory(result)

    def get_storage_dict(self, product_id: int) -> StorageDict:
        url: str = f'https://card.wb.ru/cards/detail?spp=0' \
                   f'&regions=80,64,83,4,38,33,70,69,86,30,40,48,1,22,66,31,114&pricemarginCoeff=1.0' \
                   f'&reg=0&appType=1&emp=0&locale=ru&lang=ru&curr=rub' \
                   f'&couponsGeo=2,12,7,3,6,21,16&dest=-1221148,-140294,-1751445,-364763&nm={product_id}'
        response: Response = self._session.get(url)
        response.raise_for_status()
        json_data: any = response.json()
        if 'data' not in json_data \
                or 'products' not in json_data['data'] or len(json_data['data']['products']) < 1:
            return StorageDict()
        product_data = json_data['data']['products'][0]
        if 'sizes' not in product_data and 'colors' not in product_data:
            return StorageDict()
        sizes = product_data['sizes']
        storage_dict: StorageDict = StorageDict()
        for size in sizes:
            if 'stocks' not in size or 'name' not in size:
                continue
            specify_name = size['name']
            if specify_name == '':
                specify_name = 'default'
            for stock in size['stocks']:
                specified_leftover_list: list[SpecifiedLeftover] = []
                if 'qty' not in stock:
                    continue
                wh_id: int = stock['wh']
                if wh_id not in storage_dict:
                    specified_leftover_list.append(SpecifiedLeftover(specify_name, int(stock['qty'])))
                    storage_dict[wh_id] = specified_leftover_list
                else:
                    specified_leftover_list = storage_dict[wh_id]
                    specified_leftover_list.append(SpecifiedLeftover(specify_name, int(stock['qty'])))
                    storage_dict[wh_id] = specified_leftover_list
        return storage_dict
