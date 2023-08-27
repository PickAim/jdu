from datetime import datetime
from typing import Type, Iterable

from jorm.market.infrastructure import Niche, Product, HandlerType, Category, Warehouse, Address
from jorm.market.items import ProductHistoryUnit, ProductHistory
from jorm.server.providers.initializers import DataProviderInitializer
from jorm.support.types import StorageDict, SpecifiedLeftover

from jdu.providers.wildberries_providers import WildberriesDataProviderWithoutKey, WildberriesUserMarketDataProvider
from tests.basic_db_test import BasicDBTest


class TestWildberriesDataProviderWithoutKeyImpl(WildberriesDataProviderWithoutKey):
    def get_category_and_niche(self, product_id: int) -> tuple[str, str] | None:
        return BasicDBTest.test_category_name, BasicDBTest.test_niche_name

    def get_top_request_by_marketplace_query(self, search_period: str = 'month', number_top: int = 1000,
                                             search_query: str = '') -> dict[str, int] | None:
        pass

    def __init__(self, data_provider_initializer_class: Type[DataProviderInitializer]):
        super().__init__(data_provider_initializer_class)

    def __del__(self):
        self.session.close()

    def get_categories_names(self, category_num=10) -> list[str]:
        category_names_list: list[str] = []
        for i in range(category_num):
            category_names_list.append('Category_' + i.__str__())
        return category_names_list

    def get_categories(self, category_names_list) -> list[Category]:
        category_list: list[Category] = []
        for category_name in category_names_list:
            category_list.append(Category(category_name))
        return category_list

    def get_niches_names(self, category: str, niche_num: int = 10) -> list[str]:
        niche_names_list: list[str] = []
        for i in range(niche_num):
            niche_names_list.append(f'Niche_{i.__str__()} in {category}')
        return niche_names_list

    def get_niches(self, niche_names_list) -> list[Niche]:
        niche_list = []
        for niche_name in niche_names_list:
            niche_list.append(Niche(niche_name, {
                HandlerType.MARKETPLACE: 0,
                HandlerType.PARTIAL_CLIENT: 0,
                HandlerType.CLIENT: 0}, 0))
        return niche_list

    def get_niche(self, niche_name: str) -> Niche:
        return Niche(f'{niche_name}_test_jorm', {
            HandlerType.MARKETPLACE: 0,
            HandlerType.PARTIAL_CLIENT: 0,
            HandlerType.CLIENT: 0}, 0)

    def get_products_globals_ids(self, niche: str, products_count: int = -1) -> set[int]:
        return {product_global_id for product_global_id in range(2, 11)}

    async def load_all_product_niche(self) -> list[Product]:
        pass

    def get_products(self, niche_name: str, category_name: str, products_global_ids: Iterable[int]) -> list[Product]:
        products_base = self.get_base_products(products_global_ids)
        for product in products_base:
            product.niche_name = niche_name
            product.category_name = category_name
        return products_base

    def get_base_products(self, products_global_ids: Iterable[int]) -> list[Product]:
        products_list: list[Product] = []
        for product_id in range(2, 11):
            products_list.append(
                Product(f"Name#{product_id}", product_id, product_id, 0,
                        "brand", "seller", BasicDBTest.test_niche_name,
                        BasicDBTest.test_category_name, ProductHistory())
            )
        return products_list

    def get_product_price_history(self, product_id: int) -> ProductHistory:
        units = [ProductHistoryUnit(
            i * 10, datetime.utcnow(), StorageDict()) for i in range(1, 11)]
        return ProductHistory(units)

    def get_storage_dict(self, product_id: int) -> StorageDict:
        storage_dict: StorageDict = StorageDict()
        specified_leftover_list: list[SpecifiedLeftover] = []
        for i in range(10):
            specified_leftover_list.append(SpecifiedLeftover('SpecifyName_' + i.__str__(), i))
            storage_dict[i] = specified_leftover_list
        return storage_dict


class TestWildberriesUserMarketDataProviderImpl(WildberriesUserMarketDataProvider):
    def get_user_products(self) -> list[int]:
        return [i for i in range(0, 10)]

    def __init__(self, api_key: str, data_provider_initializer_class: Type[DataProviderInitializer]):
        super().__init__(api_key, data_provider_initializer_class)

    def get_warehouses(self) -> list[Warehouse]:
        warehouses: list[Warehouse] = []
        for i in range(2, 12):
            warehouses.append(
                Warehouse('warehouse_' + i.__str__(), i, HandlerType.MARKETPLACE, Address('Address_' + i.__str__())))
        return warehouses

    def get_nearest_keywords(self, word: str) -> list[str]:
        return ["word", "word", "word"]

    def __del__(self):
        self.session.close()
