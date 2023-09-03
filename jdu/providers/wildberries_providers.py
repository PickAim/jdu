import asyncio
import logging
import time
from abc import ABC
from asyncio import AbstractEventLoop, Task
from datetime import datetime
from typing import Type, Iterable

import aiohttp
from jorm.market.infrastructure import Product, Category, Niche, HandlerType, Warehouse, Address
from jorm.market.items import ProductHistoryUnit, ProductHistory
from jorm.server.providers.initializers import DataProviderInitializer
from jorm.server.providers.providers import UserMarketDataProvider, DataProviderWithKey, DataProviderWithoutKey
from jorm.support.types import StorageDict, SpecifiedLeftover

from jdu.support.loggers import LOADING_LOGGER
from jdu.support.sorters import score_object_names, sort_by_len_alphabet
from jdu.support.types import ProductInfo
from jdu.support.utils import split_to_batches
from jdu.support.wildberries_utils import calculate_basket_domain_part


class WildberriesUserMarketDataProvider(UserMarketDataProvider, ABC):
    def __init__(self, api_key: str, data_provider_initializer_class: Type[DataProviderInitializer]):
        super().__init__(api_key, data_provider_initializer_class)


class WildberriesUserMarketDataProviderImpl(WildberriesUserMarketDataProvider):
    def __init__(self, api_key: str, data_provider_initializer_class: Type[DataProviderInitializer]):
        super().__init__(api_key, data_provider_initializer_class)

    def get_warehouses(self) -> list[Warehouse]:
        warehouses: list[Warehouse] = []
        url = 'https://suppliers-api.wildberries.ru/api/v3/offices'
        json_code = self.get_authorized_request_json(url)
        for warehouse in json_code:
            if any(k not in warehouse for k in ("name", "id", "address")):
                continue
            warehouses.append(
                Warehouse(warehouse['name'], warehouse['id'], HandlerType.MARKETPLACE, warehouse['address']))
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

    def get_user_products(self) -> list[int]:
        products_globals_ids: list[int] = []
        url_api = f'https://suppliers-api.wildberries.ru/public/api/v1/info?quantity=0'

        json_code_from_api = self.get_authorized_request_json(url_api)
        for data in json_code_from_api:
            products_globals_ids.append(data['nmId'])

        return products_globals_ids

    def get_user_warehouses(self) -> list[Warehouse]:
        warehouses: list[Warehouse] = []
        url = f'https://suppliers-api.wildberries.ru/api/v3/warehouses'
        json_code = self.get_authorized_request_json(url)
        for warehouse in json_code:
            if any(k not in warehouse for k in ("name", "id")):
                continue
            warehouses.append(Warehouse(warehouse['name'], warehouse['id'], HandlerType.CLIENT, Address('')))
        return warehouses


class WildberriesDataProviderWithKey(DataProviderWithKey):
    def __init__(self, api_key: str, data_provider_initializer_class: Type[DataProviderInitializer]):
        super().__init__(api_key, data_provider_initializer_class)

    def get_parents(self) -> list[str]:
        parent_categories: list[str] = []
        url = 'https://suppliers-api.wildberries.ru/content/v1/object/parent/all'
        json_code = self.get_authorized_request_json(url)
        for data in json_code['data']:
            parent_categories.append(data['name'])
        return parent_categories


class WildberriesDataProviderStatisticsImpl(WildberriesDataProviderWithKey):
    def __init__(self, api_key: str, data_provider_initializer_class: Type[DataProviderInitializer]):
        super().__init__(api_key, data_provider_initializer_class)


class WildberriesDataProviderAdsImpl(WildberriesDataProviderWithKey):
    def __init__(self, api_key: str, data_provider_initializer_class: Type[DataProviderInitializer]):
        super().__init__(api_key, data_provider_initializer_class)


class WildberriesDataProviderWithoutKey(DataProviderWithoutKey, ABC):
    def __init__(self, data_provider_initializer_class: Type[DataProviderInitializer]):
        super().__init__(data_provider_initializer_class)


class WildberriesDataProviderWithoutKeyImpl(WildberriesDataProviderWithoutKey):

    def __init__(self, data_provider_initializer_class: Type[DataProviderInitializer]):
        super().__init__(data_provider_initializer_class)
        self.LOGGER = logging.getLogger(LOADING_LOGGER)

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
            niche_list.append(Niche(niche_name, self.commission_resolver.get_commission_for_niche_mapped(niche_name),
                                    self.commission_resolver.get_return_percent_for(niche_name)))

        return niche_list

    def get_products_globals_ids(self, niche: str, products_count: int = -1) -> set[int]:
        page_iterator: int = 1
        product_counter: int = 0
        products_global_ids: set[int] = set()
        self.LOGGER.info("Start products info mapping.")
        start_time = time.time()
        while True:
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
                    return products_global_ids
                if any(k not in product for k in ["id", "name", "salePriceU"]):
                    continue
                products_global_ids.add(product['id'])
                product_counter += 1
            page_iterator += 1
        self.LOGGER.info(f"End mapping products info. {len(products_global_ids)} "
                         f"was mapped in {time.time() - start_time} seconds.")
        return products_global_ids

    def get_products(self, niche_name: str, category_name: str, products_global_ids: Iterable[int]) -> list[Product]:
        base_products = self.get_base_products(products_global_ids)
        for product in base_products:
            product.niche_name = niche_name
            product.category_name = category_name
        return base_products

    def get_base_products(self, products_global_ids: Iterable[int]) -> list[Product]:
        self.LOGGER.info("Start products loading.")
        start_time = time.time()
        loop: AbstractEventLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        products_global_ids = list(products_global_ids)
        result_products = loop.run_until_complete(
            self.__async_product_batch_gathering(products_global_ids)
        )
        loop.run_until_complete(asyncio.sleep(0.25))
        loop.close()
        self.LOGGER.info(f"End products loading. {len(products_global_ids)} "
                         f"was loaded in {time.time() - start_time} seconds..")
        return result_products

    async def __async_product_batch_gathering(self, products_global_ids: list[int]) -> list[Product]:
        tasks = []
        products_global_ids_batches = split_to_batches(products_global_ids, self.THREAD_TASK_COUNT)
        for products_global_ids_batch in products_global_ids_batches:
            tasks.append(
                self.__load_all_product_niche(
                    products_global_ids_batch
                )
            )
        execution_results = await asyncio.gather(*tasks)
        result: list[Product] = []
        for result_list in execution_results:
            result.extend(result_list)
        return result

    async def __load_all_product_niche(self, products_global_ids: list[int]) -> list[Product]:
        tasks: list[Task] = []
        for product_id in products_global_ids:
            task = asyncio.create_task(self.__get_product(product_id))
            tasks.append(task)
        try:
            products = await asyncio.gather(*tasks)
            products = [product for product in products if product is not None]
            return products
        except Exception as e:
            for task in tasks:
                task.cancel()
            raise e

    async def __get_product(self, product_id: int, loop=None, connector=None) -> Product | None:
        cost_history_url: str = self.__get_product_history_url(product_id)
        storage_url: str = f'https://card.wb.ru/cards/detail?' \
                           f'dest=-1221148,-140294,-1751445,-364763' \
                           f'&nm={product_id}'
        async with aiohttp.ClientSession() if loop is None or connector is None \
                else aiohttp.ClientSession(connector=connector, loop=loop) as client_session:
            request_json = await self.get_async_request_json(cost_history_url, client_session)
            product_history_units = self.__resolve_json_to_history_units(request_json)
            request_json = await self.get_async_request_json(storage_url, client_session)
            product_info = self.__resolve_json_to_product_info(request_json)
            storage_dict = self.__resolve_json_to_storage_dict(request_json)
            product_history_units.append(ProductHistoryUnit(product_info.price, datetime.utcnow(), storage_dict))

        await client_session.close()
        if product_info is not None:
            return Product(product_info.name, product_info.price, product_info.global_id, product_info.rating,
                           product_info.brand, 'seller', 'niche_name', 'category_name',
                           ProductHistory(product_history_units),
                           width=0, height=0, depth=0)
        return None

    def get_product_price_history(self, product_id: int) -> ProductHistory:
        # TODO try to extract common parts for get_product and this method
        cost_history_url: str = self.__get_product_history_url(product_id)
        storage_url: str = f'https://card.wb.ru/cards/detail?' \
                           f'dest=-1221148,-140294,-1751445,-364763' \
                           f'&nm={product_id}'
        request_json = self.get_request_json(cost_history_url)
        product_history_units = self.__resolve_json_to_history_units(request_json)
        if len(product_history_units) > 0:
            last_item = product_history_units[-1]
            request_json = self.get_request_json(storage_url)
            if isinstance(request_json, dict):
                last_item.leftover = self.__resolve_json_to_storage_dict(request_json)
        return ProductHistory(product_history_units)

    @staticmethod
    def __get_product_history_url(global_product_id: int) -> str:
        basket_domain_part = calculate_basket_domain_part(global_product_id)
        return f"https://{basket_domain_part}/info/price-history.json"

    def get_storage_dict(self, product_id: int) -> StorageDict:
        storage_url: str = f'https://card.wb.ru/cards/detail?' \
                           f'dest=-1221148,-140294,-1751445,-364763' \
                           f'&nm={product_id}'
        request_json = self.get_request_json(storage_url)
        if isinstance(request_json, dict):
            return self.__resolve_json_to_storage_dict(request_json)
        return StorageDict()

    @staticmethod
    def __resolve_json_to_product_info(request_json: dict) -> ProductInfo | None:
        if 'data' not in request_json \
                or 'products' not in request_json['data'] or len(request_json['data']['products']) < 1:
            return None
        product_data = request_json['data']['products'][0]
        product_info = ProductInfo(product_data['id'], product_data['name'], product_data['salePriceU'],
                                   product_data['brand'], product_data['rating'])
        return product_info

    @staticmethod
    def __resolve_json_to_history_units(request_json: dict) -> list[ProductHistoryUnit]:
        if request_json is None:
            return []
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

    def get_top_request_by_marketplace_query(self, search_period: str = 'month', number_top: int = 1000,
                                             search_query: str = '') -> dict[str, int] | None:
        self.LOGGER.info("Start top-request loading.")
        name_and_request_count_dict: dict[str, int] = {}
        url = f'https://trending-searches.wb.ru/api?itemsPerPage={number_top}' \
              f'&offset=0&period={search_period}&query={search_query}&sort=desc'
        json_data = self.get_request_json(url)
        if json_data['data']['count'] == 0:
            return None
        for query_from_top in json_data['data']['list']:
            name_and_request_count_dict[query_from_top['text']] = query_from_top['requestCount']
        return name_and_request_count_dict

    def get_category_and_niche(self, product_id: int) -> tuple[str, str] | None:
        url = f'https://{calculate_basket_domain_part(product_id)}/info/ru/card.json'
        json_data = self.get_request_json(url)
        if 'subj_root_name' not in json_data or 'subj_name' not in json_data:
            return None
        return json_data['subj_root_name'], json_data['subj_name']

    def get_delivery_address(self) -> dict[id, str]:
        url = 'https://static-basket-01.wb.ru/vol0/data/all-poo-fr-v6.json'
        json_data = self.get_request_json(url)
        deliveries_addresses_list: dict[id, str] = {}
        for delivery_addresses in json_data:
            for delivery_address in delivery_addresses['items']:
                deliveries_addresses_list[delivery_address['id']] = delivery_address['address']
        return deliveries_addresses_list
