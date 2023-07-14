import asyncio
import logging
import math
from abc import ABC
from asyncio import AbstractEventLoop, Task
from datetime import datetime

import aiohttp
from jorm.market.infrastructure import Product, Category, Niche, HandlerType, Warehouse
from jorm.market.items import ProductHistoryUnit, ProductHistory
from jorm.support.types import StorageDict, SpecifiedLeftover

from jdu.providers.providers import UserMarketDataProvider, DataProviderWithoutKey, DataProviderWithKey
from jdu.support.sorters import score_object_names, sort_by_len_alphabet
from jdu.support.types import ProductInfo


class WildberriesUserMarketDataProvider(UserMarketDataProvider, ABC):
    def __init__(self, api_key: str):
        super().__init__(api_key)


class WildberriesUserMarketDataProviderImpl(WildberriesUserMarketDataProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key)

    def get_warehouses(self) -> list[Warehouse]:
        warehouses: list[Warehouse] = []
        url = 'https://suppliers-api.wildberries.ru/api/v3/offices'
        json_code = self.get_authorized_request_json(url)
        for warehouse in json_code:
            if any(k not in warehouse for k in ("name", "id", "address")):
                continue
            warehouses.append(Warehouse(warehouse['name'], warehouse['id'], HandlerType.CLIENT, warehouse['address']))
        return warehouses

    def get_nearest_keywords(self, word: str) -> list[str]:
        names: list[str] = self.__get_nearest_names(word)
        scored_dict: dict[float, list[str]] = score_object_names(word, names)
        result: list[str] = []
        for score in scored_dict.keys():
            result.extend(sort_by_len_alphabet(scored_dict[score]))
        return result

    def __get_nearest_names(self, text: str) -> list[str]:
        object_name_list: list[str] = []
        url = f'https://suppliers-api.wildberries.ru/content/v1/object/all?name={text}&top=100'
        json_code = self.get_authorized_request_json(url)
        for data in json_code['data']:
            if 'objectName' not in data:
                continue
            object_name_list.append(data['objectName'])
        return object_name_list


class WildberriesDataProviderWithKey(DataProviderWithKey):
    def get_parents(self) -> list[str]:
        parent_categories: list[str] = []
        url = 'https://suppliers-api.wildberries.ru/content/v1/object/parent/all'
        json_code = self.get_authorized_request_json(url)
        for data in json_code['data']:
            parent_categories.append(data['name'])
        return parent_categories


class WildberriesDataProviderStatisticsImpl(WildberriesDataProviderWithKey):
    def __init__(self, api_key: str):
        super().__init__(api_key)


class WildberriesDataProviderAdsImpl(WildberriesDataProviderWithKey):
    def __init__(self, api_key: str):
        super().__init__(api_key)


class WildberriesDataProviderWithoutKey(DataProviderWithoutKey, ABC):
    def __init__(self):
        super().__init__()
        self.marketplace_name = 'wildberries'


class WildberriesDataProviderWithoutKeyImpl(WildberriesDataProviderWithoutKey):
    def __init__(self):
        super().__init__()
        self.LOGGER = logging.getLogger(self.__class__.__name__)

    __VOL_HOST_PARTS: dict[str, tuple[int, int]] = {
        "01": (0, 143),
        "02": (144, 287),
        "03": (288, 431),
        "04": (431, 719),
        "05": (720, 1007),
        "06": (1008, 1061),
        "07": (1062, 1115),
        "08": (1116, 1169),
        "09": (1170, 1313),
        "10": (1314, 1601),
        "11": (1602, 1655),
        "12": (1656, 1919),
        "13": (1920, 10000)
    }

    def get_categories_names(self, category_num=-1) -> list[str]:
        category_names_list: list[str] = []
        url: str = 'https://static-basket-01.wb.ru/vol0/data/subject-base.json'
        json_data = self.get_request_json(url)
        for i, data in enumerate(json_data):
            if category_num != -1 and i >= category_num:
                break
            if 'name' not in data:
                continue
            category_names_list.append(data['name'])
        return category_names_list

    @staticmethod
    def get_categories(category_names_list: list[str]) -> list[Category]:
        categories_list: list[Category] = []
        for category_name in category_names_list:
            categories_list.append(Category(category_name))
        return categories_list

    def get_niches_names(self, category_name: str, niche_num: int = -1) -> list[str]:
        niche_names: list[str] = []
        niche_counter: int = 0
        url: str = 'https://static-basket-01.wb.ru/vol0/data/subject-base.json'
        json_data = self.get_request_json(url)
        for data in json_data:
            if data['name'] != category_name:
                continue
            for niche in data['childs']:
                if niche_num != -1 and niche_counter >= niche_num:
                    return niche_names
                niche_names.append(niche['name'])
                niche_counter += 1
        return niche_names

    def get_niches(self, niche_names_list):
        niche_list: list[Niche] = []
        for niche_name in niche_names_list:
            niche_list.append(Niche(niche_name, {
                HandlerType.MARKETPLACE: 0,  # TODO think about constants loading
                HandlerType.PARTIAL_CLIENT: 0,
                HandlerType.CLIENT: 0}, 0))
        return niche_list

    def get_products_mapped_info(self, niche: str, products_count: int = -1) -> set[ProductInfo]:
        page_iterator: int = 1
        product_counter: int = 0
        products_info: set[ProductInfo] = set()
        self.LOGGER.info("Start products info mapping.")
        while True:
            # TODO think about it https://search-goods.wildberries.ru/search?query=
            url: str = f'https://search.wb.ru/exactmatch/ru/common/v4/search' \
                       f'?appType=1' \
                       f'&dest=-1257786' \
                       f'&page={page_iterator}' \
                       f'&query={niche}' \
                       f'&resultset=catalog' \
                       f'&sort=popular' \
                       f'&suppressSpellcheck=false'
            try:
                json_code = self.get_request_json(url)
            except Exception:
                self.reset_session()
                continue
            if 'data' not in json_code or 'products' not in json_code['data']:
                break
            if len(json_code['data']['products']) == 0:
                break
            for product in json_code['data']['products']:
                if products_count != -1 and product_counter >= products_count:
                    return products_info
                if any(k not in product for k in ["id", "name", "priceU"]):
                    continue
                product_info = ProductInfo(product['id'], product['name'], product['priceU'])
                products_info.add(product_info)
                product_counter += 1
            page_iterator += 1
        self.LOGGER.info(f"End mapping products info. {len(products_info)} was mapped.")
        return products_info

    def get_products(self, niche_name: str,
                     category_name: str,
                     products_info: list[ProductInfo]) -> list[Product]:
        result_products = []
        self.LOGGER.info("Start products loading.")
        for i in range(0, max(len(products_info) - self.THREAD_TASK_COUNT + 1, 1), self.THREAD_TASK_COUNT):
            loop: AbstractEventLoop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result_products.extend(
                loop.run_until_complete(
                    self.__load_all_product_niche(
                        products_info[i:i + self.THREAD_TASK_COUNT],
                        niche_name, category_name
                    )
                )
            )
            loop.close()
        self.LOGGER.info(f"End products loading. {len(products_info)} was loaded.")
        return result_products

    async def __load_all_product_niche(self,
                                       products_info: list[ProductInfo],
                                       niche_name: str,
                                       category_name: str) -> list[Product]:
        products: list[Product] = []
        tasks: list[Task] = []
        for product_info in products_info:
            task = asyncio.create_task(self.__get_product_price_history(product_info.global_id))
            tasks.append(task)
        product_price_histories = await asyncio.gather(*tasks)
        for i, product_info in enumerate(products_info):
            products.append(Product(product_info.name, product_info.price, product_info.global_id, 0,
                                    "brand", "seller", niche_name, category_name,
                                    history=product_price_histories[i], width=0, height=0, depth=0))
        return products

    async def __get_product_price_history(self, product_id: int, loop=None, connector=None) -> ProductHistory:
        cost_history_url: str = self.get_product_history_url(product_id)
        storage_url: str = f'https://card.wb.ru/cards/detail?' \
                           f'dest=-1221148,-140294,-1751445,-364763' \
                           f'&nm={product_id}'
        async with aiohttp.ClientSession() if loop is None or connector is None \
                else aiohttp.ClientSession(connector=connector, loop=loop) as client_session:
            request_json = await self.get_async_request_json(cost_history_url, client_session)
            product_history_units = self.__resolve_json_to_history_units(request_json)
            if len(product_history_units) > 0:
                last_item = product_history_units[len(product_history_units) - 1]
                request_json = await self.get_async_request_json(storage_url, client_session)
                last_item.leftover = self.__resolve_json_to_storage_dict(request_json)
        await client_session.close()
        return ProductHistory(product_history_units)

    def get_product_price_history(self, product_id: int) -> ProductHistory:
        cost_history_url: str = self.get_product_history_url(product_id)
        storage_url: str = f'https://card.wb.ru/cards/detail?' \
                           f'dest=-1221148,-140294,-1751445,-364763' \
                           f'&nm={product_id}'
        request_json = self.get_request_json(cost_history_url)
        product_history_units = self.__resolve_json_to_history_units(request_json)
        if len(product_history_units) > 0:
            last_item = product_history_units[len(product_history_units) - 1]
            request_json = self.get_request_json(storage_url)
            if isinstance(request_json, dict):
                last_item.leftover = self.__resolve_json_to_storage_dict(request_json)
        return ProductHistory(product_history_units)

    def get_product_history_url(self, global_product_id: int) -> str:
        basket_domain_part = self.__calculate_basket_domain_part(global_product_id)
        return f"https://{basket_domain_part}/info/price-history.json"

    def __calculate_basket_domain_part(self, global_product_id: int) -> str:
        vol_number = math.floor(global_product_id / 1e5)
        basket_url_part = self.__get_basket_host_part(vol_number)
        part_number = math.floor(global_product_id / 1e3)
        return f"{basket_url_part}/vol{vol_number}/part{part_number}/{global_product_id}"

    @staticmethod
    def __get_basket_host_part(basket_number: int) -> str:
        result_basket_idx = "13"
        for basket_idx in WildberriesDataProviderWithoutKeyImpl.__VOL_HOST_PARTS:
            lower_basket_frontier, upper_basket_frontier = WildberriesDataProviderWithoutKeyImpl.__VOL_HOST_PARTS[
                basket_idx]
            if lower_basket_frontier <= basket_number <= upper_basket_frontier:
                result_basket_idx = basket_idx
                break
        return f"basket-{result_basket_idx}.wb.ru"

    def get_storage_dict(self, product_id: int) -> StorageDict:
        storage_url: str = f'https://card.wb.ru/cards/detail?' \
                           f'dest=-1221148,-140294,-1751445,-364763' \
                           f'&nm={product_id}'
        request_json = self.get_request_json(storage_url)
        if isinstance(request_json, dict):
            return self.__resolve_json_to_storage_dict(request_json)
        return StorageDict()

    @staticmethod
    def __resolve_json_to_history_units(request_json: dict) -> list[ProductHistoryUnit]:
        result_units: list[ProductHistoryUnit] = []
        for item in request_json:
            if 'price' not in item \
                    or 'RUB' not in item['price'] \
                    or 'dt' not in item:
                continue
            result_units.append(ProductHistoryUnit(item['price']['RUB'],
                                                   datetime.fromtimestamp(item['dt']), StorageDict()))
        return result_units

    @staticmethod
    def __resolve_json_to_storage_dict(json_code) -> StorageDict:
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
                if 'qty' not in stock or 'wh' not in stock:
                    continue
                wh_id: int = stock['wh']
                if wh_id not in storage_dict:
                    storage_dict[wh_id] = []
                specified_leftover_list = storage_dict[wh_id]
                specified_leftover_list.append(SpecifiedLeftover(specify_name, int(stock['qty'])))
                storage_dict[wh_id] = specified_leftover_list
        return storage_dict
