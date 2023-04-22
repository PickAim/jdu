import asyncio
from asyncio import AbstractEventLoop, Task
from datetime import datetime

import aiohttp
from aiohttp import ClientSession
from jorm.market.infrastructure import Product, Category, Niche, HandlerType
from jorm.market.items import ProductHistoryUnit, ProductHistory
from jorm.support.types import StorageDict, SpecifiedLeftover
from requests import Response

from jdu.providers import WildBerriesDataProviderWithoutKey, WildBerriesDataProviderWithKey
from jdu.utils.sorters import score_object_names, sort_by_len_alphabet


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
        response: Response = self._session.get(url)
        response.raise_for_status()
        json_data: any = response.json()
        category_iterator: int = 1
        for data in json_data:
            category_names_list.append(data['name'])
            category_iterator += 1
            if category_num != -1 and category_iterator > category_num:
                break
        return category_names_list

    def get_categories(self, category_names_list: [str]) -> list[Category]:
        categories_list: list[Category] = []
        for category_name in category_names_list:
            categories_list.append(Category(category_name))

        return categories_list

    def get_niches_names(self, name_category: str, niche_num: int = -1) -> list[str]:
        niche_names_list: list[str] = []
        niche_iterator: int = 1
        url: str = 'https://static-basket-01.wb.ru/vol0/data/subject-base.json'
        response: Response = self._session.get(url)
        response.raise_for_status()
        json_data: any = response.json()
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
        # TODO Получая ниши из частотного анализа запросов, мы не контролируем Category(Всё улетит в OtherCategory)
        # TODO Предложение: с помощью nearest_names получать близкие имена ниш. находя близкое имя ниши определяем Категорию
        niche_list: list[Niche] = []
        for niche_name in niche_names_list:
            niche_list.append(Niche(niche_name, {
                HandlerType.MARKETPLACE: 0,
                HandlerType.PARTIAL_CLIENT: 0,
                HandlerType.CLIENT: 0}, 0))
        return niche_list

    def get_product_name_id_cost_list(self, niche: str, pages_num: int, products_count: int) -> list[
        tuple[str, int, int]]:
        page_iterator: int = 1
        name_id_cost_list: list[tuple[str, int, int]] = []
        while True:
            url: str = f'https://search.wb.ru/exactmatch/ru/common/v4/search?' \
                       f'appType=1' \
                       f'&dest=-1221148,-140294,-1751445,-364763' \
                       f'&lang=ru' \
                       f'&query={niche}' \
                       f'&resultset=catalog' \
                       f'&sort=popular' \
                       f'&page={page_iterator}'
            request: Response = self._session.get(
                url
            )
            if request.status_code != 200:
                break
            json_code: any = request.json()
            if 'data' not in json_code:
                break
            product_iterator: int = 0
            for product in json_code['data']['products']:
                if products_count != -1 and product_iterator > products_count:
                    break
                name_id_cost_list.append(
                    (product['name'], product['id'], product['priceU']))
                product_iterator += 1
            page_iterator += 1
            if pages_num != -1 and page_iterator > pages_num:
                break
        return name_id_cost_list

    async def __load_all_product_niche(self, name_id_cost_list) -> list[Product]:
        products: list[Product] = []
        async with aiohttp.ClientSession() as session:
            tasks: list[Task] = []
            for name_id_cost in name_id_cost_list:
                task = asyncio.create_task(self.__get_product_price_history(session, name_id_cost[1]))
                tasks.append(task)
            product_price_history_list: any = await asyncio.gather(*tasks)
            for index in range(len(name_id_cost_list)):
                products.append(Product(name_id_cost_list[index][0],
                                        name_id_cost_list[index][2],
                                        name_id_cost_list[index][1], 0,
                                        product_price_history_list[index], width=0, height=0, depth=0))
        await session.close()
        return products

    def get_products(self, niche: str, pages_num: int = -1, products_count: int = -1) -> list[Product]:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        loop: AbstractEventLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        name_id_cost_list: list[tuple[str, int, int]] = self.get_product_name_id_cost_list(niche, pages_num,
                                                                                           products_count)
        products: list[Product] = loop.run_until_complete(self.__load_all_product_niche(name_id_cost_list))
        loop.close()
        return products

    def get_price_history(self, product_id: int) -> ProductHistory:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        loop: AbstractEventLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        product_history: ProductHistory = loop.run_until_complete(self.__get_price_history_with_loop(loop, product_id))
        loop.close()
        return product_history

    async def __get_price_history_with_loop(self, loop, product_id: int) -> ProductHistory:
        connector = aiohttp.TCPConnector(limit=10)
        async with aiohttp.ClientSession(connector=connector, loop=loop) as session:
            product_history: ProductHistory = await self.__get_product_price_history(session, product_id)
            return product_history

    async def __get_product_price_history(self, client_session: ClientSession, product_id: int) -> ProductHistory:
        url: str = f'https://wbx-content-v2.wbstatic.net/price-history/{product_id}.json?'
        result: list[ProductHistoryUnit] = []
        async with client_session.get(url=url) as request:
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
        url: str = f'https://card.wb.ru/cards/detail?' \
                   f'dest=-1221148,-140294,-1751445,-364763' \
                   f'&nm={product_id}'
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
                if 'qty' not in stock:
                    continue
                wh_id: int = stock['wh']
                if wh_id not in storage_dict:
                    storage_dict[wh_id] = []
                specified_leftover_list = storage_dict[wh_id]
                specified_leftover_list.append(SpecifiedLeftover(specify_name, int(stock['qty'])))
                storage_dict[wh_id] = specified_leftover_list

        return storage_dict
