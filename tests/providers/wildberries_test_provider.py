from datetime import datetime
from typing import Type

from jorm.market.infrastructure import Niche, Product, HandlerType, Category, Warehouse, Address
from jorm.market.items import ProductHistoryUnit, ProductHistory
from jorm.support.types import StorageDict, SpecifiedLeftover

from jdu.providers.initializers import DataProviderInitializer
from jdu.providers.wildberries_providers import WildberriesDataProviderWithoutKey, WildberriesUserMarketDataProvider
from jdu.support.types import ProductInfo


class WildBerriesDataProviderWithoutKeyImplTest(WildberriesDataProviderWithoutKey):
    def __init__(self, data_provider_initializer_class: Type[DataProviderInitializer]):
        super().__init__(data_provider_initializer_class)

    def __del__(self):
        self.session.close()

    def get_categories_names(self, category_num=-1) -> list[str]:
        category_names_list: list[str] = []
        for i in range(category_num):
            category_names_list.append('Category_' + i.__str__())
        return category_names_list

    def get_categories(self, category_names_list) -> list[Category]:
        category_list: list[Category] = []
        for category_name in category_names_list:
            category_list.append(Category(category_name))
        return category_list

    def get_niches_names(self, category, niche_num=-1) -> list[str]:
        niche_names_list: list[str] = []
        for i in range(niche_num):
            niche_names_list.append('Niche_' + i.__str__())
        return niche_names_list

    def get_niches(self, niche_names_list) -> list[Niche]:
        niche_list = []
        for niche_name in niche_names_list:
            niche_list.append(Niche(niche_name, {
                HandlerType.MARKETPLACE: 0,
                HandlerType.PARTIAL_CLIENT: 0,
                HandlerType.CLIENT: 0}, 0))
        return niche_list

    def get_products_mapped_info(self, niche: str, products_count: int = -1) -> set[ProductInfo]:
        products_info: set[ProductInfo] = set()
        for i in range(10):
            products_info.add(ProductInfo(i, 'Product_' + i.__str__(), i))
        return products_info

    async def load_all_product_niche(self) -> list[Product]:
        pass

    def get_products(self, niche_name: str, category_name: str,
                     products_info: list[ProductInfo]) -> list[Product]:
        products_list: list[Product] = []
        for product_info in products_info:
            products_list.append(
                Product(product_info.name, product_info.price, product_info.global_id, 0,
                        "brand", "seller", niche_name, category_name, ProductHistory())
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


class WildberriesUserMarketDataProviderImplTest(WildberriesUserMarketDataProvider):
    def __init__(self, data_provider_initializer_class: Type[DataProviderInitializer]):
        super().__init__("api-key", data_provider_initializer_class)

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
