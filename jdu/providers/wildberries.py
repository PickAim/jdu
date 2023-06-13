import asyncio
from asyncio import AbstractEventLoop, Task
from datetime import datetime

import aiohttp
from jorm.market.infrastructure import Product, Category, Niche, HandlerType
from jorm.market.items import ProductHistoryUnit, ProductHistory
from jorm.support.types import StorageDict, SpecifiedLeftover
from requests import Response

from jdu.providers import WildBerriesDataProviderWithoutKey, WildBerriesDataProviderWithKey
from jdu.support.sorters import score_object_names, sort_by_len_alphabet
from jdu.support.utils import get_async_request_json, get_request_json


class WildBerriesDataProviderStandardImpl(WildBerriesDataProviderWithKey):

    def __init__(self, api_key: str):
        super().__init__(api_key)

    def __get_nearest_names(self, text: str) -> list[str]:
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
        names: list[str] = self.__get_nearest_names(word)
        scored_dict: dict[float, list[str]] = score_object_names(word, names)
        result: list[str] = []
        for score in scored_dict.keys():
            result.extend(sort_by_len_alphabet(scored_dict[score]))
        return result


class WildBerriesDataProviderStatisticsImpl(WildBerriesDataProviderWithKey):

    def __init__(self, api_key: str):
        super().__init__(api_key)


class WildBerriesDataProviderAdsImpl(WildBerriesDataProviderWithKey):

    def __init__(self, api_key: str):
        super().__init__(api_key)


class WildBerriesDataProviderWithoutKeyImpl(WildBerriesDataProviderWithoutKey):

    def __init__(self):
        super().__init__()

    def get_categories_names(self, category_num=-1) -> list[str]:
        category_names_list: list[str] = []
        url: str = 'https://static-basket-01.wb.ru/vol0/data/subject-base.json'
        json_data = get_request_json(url, self._session)
        category_iterator: int = 0
        for data in json_data:
            category_names_list.append(data['name'])
            category_iterator += 1
            if category_num != -1 and category_iterator >= category_num:
                break
        return category_names_list

    @staticmethod
    def get_categories(category_names_list: list[str]) -> list[Category]:
        categories_list: list[Category] = []
        for category_name in category_names_list:
            categories_list.append(Category(category_name))
        return categories_list

    def get_niches_names(self, name_category: str, niche_num: int = -1) -> list[str]:
        niche_names_list: list[str] = []
        niche_iterator: int = 1
        url: str = 'https://static-basket-01.wb.ru/vol0/data/subject-base.json'
        json_data = get_request_json(url, self._session)
        for data in json_data:
            if data['name'] == name_category:
                for niche in data['childs']:
                    niche_names_list.append(niche['name'])
                    niche_iterator += 1
                    if niche_num != -1 and niche_iterator > niche_num:
                        break
                break
        return niche_names_list

    def get_niches(self, niche_names_list):
        niche_list: list[Niche] = []
        for niche_name in niche_names_list:
            niche_list.append(Niche(niche_name, {
                HandlerType.MARKETPLACE: 0,
                HandlerType.PARTIAL_CLIENT: 0,
                HandlerType.CLIENT: 0}, 0))
        return niche_list

    def get_products_id_to_name_cost_dict(self, niche: str, products_count: int = -1) -> dict[int, tuple[str, int]]:
        page_iterator: int = 1
        product_iterator: int = 0
        id_to_name_cost_dict: dict[int, tuple[str, int]] = {}
        while True:
            url: str = f'https://search.wb.ru/exactmatch/ru/common/v4/search?' \
                       f'appType=1' \
                       f'&dest=-1221148,-140294,-1751445,-364763' \
                       f'&lang=ru' \
                       f'&query={niche}' \
                       f'&resultset=catalog' \
                       f'&sort=popular' \
                       f'&page={page_iterator}'
            json_code = get_request_json(url, self._session)
            if 'data' not in json_code:
                break
            for product in json_code['data']['products']:
                if products_count != -1 and product_iterator >= products_count:
                    return id_to_name_cost_dict
                id_to_name_cost_dict[product['id']] = (product['name'], product['priceU'])
                product_iterator += 1
            page_iterator += 1
        return id_to_name_cost_dict

    def get_products(self, niche_name: str, category_name: str, id_name_cost_list: list[tuple[int, str, int]]) -> list[
        Product]:
        result_products = []
        for i in range(0, len(id_name_cost_list) - self.THREAD_TASK_COUNT + 1, self.THREAD_TASK_COUNT):
            loop: AbstractEventLoop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result_products.extend(
                loop.run_until_complete(
                    self.__load_all_product_niche(id_name_cost_list[i:i + self.THREAD_TASK_COUNT], niche_name,
                                                  category_name)
                )
            )
            loop.close()
        return result_products

    async def __load_all_product_niche(self, id_to_name_cost_dict: list[tuple[int, str, int]], niche_name: str,
                                       category_name: str) -> list[
        Product]:
        products: list[Product] = []
        tasks: list[Task] = []
        for global_id in id_to_name_cost_dict:
            task = asyncio.create_task(self.__get_product_price_history(global_id[0]))
            tasks.append(task)
        product_price_history_list = await asyncio.gather(*tasks)
        for index, id_name_cost in enumerate(id_to_name_cost_dict):
            products.append(Product(id_name_cost[1], id_name_cost[2], id_name_cost[0], 0,
                                    "brand", "seller", niche_name, category_name,
                                    product_price_history_list[index], width=0, height=0, depth=0))
        return products

    async def __get_product_price_history(self, product_id: int, loop=None, connector=None) -> ProductHistory:
        cost_history_url: str = f'https://wbx-content-v2.wbstatic.net/price-history/{product_id}.json?'
        storage_url: str = f'https://card.wb.ru/cards/detail?' \
                           f'dest=-1221148,-140294,-1751445,-364763' \
                           f'&nm={product_id}'
        async with aiohttp.ClientSession() if loop is None or connector is None \
                else aiohttp.ClientSession(connector=connector, loop=loop) as client_session:
            request_json = await get_async_request_json(cost_history_url, client_session)
            result = self.__resolve_json_to_history_units(request_json)
            if len(result) > 0:
                last_item = result[len(result) - 1]
                request_json = await get_async_request_json(storage_url, client_session)
                if isinstance(request_json, dict):
                    last_item.leftover = self.__resolve_json_to_storage_dict(request_json)
        await client_session.close()
        return ProductHistory(result)

    def get_product_price_history(self, product_id: int) -> ProductHistory:
        cost_history_url: str = f'https://wbx-content-v2.wbstatic.net/price-history/{product_id}.json?'
        storage_url: str = f'https://card.wb.ru/cards/detail?' \
                           f'dest=-1221148,-140294,-1751445,-364763' \
                           f'&nm={product_id}'
        request_json = get_request_json(cost_history_url, self._session)
        result = self.__resolve_json_to_history_units(request_json)
        if len(result) > 0:
            last_item = result[len(result) - 1]
            request_json = get_request_json(storage_url, self._session)
            if isinstance(request_json, dict):
                last_item.leftover = self.__resolve_json_to_storage_dict(request_json)
        return ProductHistory(result)

    def get_storage_dict(self, product_id: int) -> StorageDict:
        storage_url: str = f'https://card.wb.ru/cards/detail?' \
                           f'dest=-1221148,-140294,-1751445,-364763' \
                           f'&nm={product_id}'
        request_json = get_request_json(storage_url, self._session)
        if isinstance(request_json, dict):
            return self.__resolve_json_to_storage_dict(request_json)
        return StorageDict()

    @staticmethod
    def __resolve_json_to_history_units(request_json: dict) -> list[ProductHistoryUnit]:
        result: list[ProductHistoryUnit] = []
        for item in request_json:
            if 'price' not in item \
                    or 'RUB' not in item['price'] \
                    or 'dt' not in item:
                continue
            result.append(ProductHistoryUnit(item['price']['RUB'],
                                             datetime.fromtimestamp(item['dt']), StorageDict()))
        return result

    @staticmethod
    def __resolve_json_to_storage_dict(json_code: dict) -> StorageDict:
        if 'data' not in json_code \
                or 'products' not in json_code['data'] or len(json_code['data']['products']) < 1:
            return StorageDict()
        product_data = json_code['data']['products'][0]
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
                if 'qty' not in stock:
                    continue
                wh_id: int = stock['wh']
                if wh_id not in storage_dict:
                    storage_dict[wh_id] = []
                specified_leftover_list = storage_dict[wh_id]
                specified_leftover_list.append(SpecifiedLeftover(specify_name, int(stock['qty'])))
                storage_dict[wh_id] = specified_leftover_list
        return storage_dict
