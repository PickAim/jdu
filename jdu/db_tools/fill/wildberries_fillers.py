from abc import abstractmethod
from typing import Type

from jdu.db_tools.fill.db_fillers import StandardDBFiller, SimpleDBFiller
from jdu.db_tools.fill.initializers import DBFillerInitializer
from jdu.providers.wildberries_providers import WildberriesDataProviderWithoutKey, WildberriesUserMarketDataProvider
from jdu.support.types import ProductInfo
from jorm.market.infrastructure import Category, Niche, Warehouse, HandlerType, Address
from jorm.market.items import Product
from jorm.support.constants import DEFAULT_CATEGORY_NAME
from sqlalchemy.orm import Session


class WildberriesDBFillerWithKey(SimpleDBFiller):
    def __init__(self, session: Session,
                 provider_with_key: WildberriesUserMarketDataProvider,
                 db_initializer_class: Type[DBFillerInitializer]):
        super().__init__(session, db_initializer_class)
        self.provider_with_key: WildberriesUserMarketDataProvider = provider_with_key

    @abstractmethod
    def fill_warehouse(self) -> None:
        pass


class WildberriesDBFillerImpl(StandardDBFiller):
    def __init__(self, session: Session,
                 provider_without_key: WildberriesDataProviderWithoutKey,
                 db_initializer_class: Type[DBFillerInitializer]):
        super().__init__(session, db_initializer_class)
        self.provider_without_key = provider_without_key

    def fill_categories(self, category_num: int = -1):
        categories_names: list[str] = self.provider_without_key.get_categories_names(category_num)
        filtered_categories_names: list[str] = \
            self.category_service.filter_existing_names(categories_names, self.marketplace_id)
        categories: list[Category] = self.provider_without_key.get_categories(filtered_categories_names)
        self.category_service.create_all(categories, self.marketplace_id)

    def fill_niches(self, niche_num: int = -1):
        categories: dict[int, Category] = self.category_service.find_all_in_marketplace(self.marketplace_id)
        for category_id in categories:
            niches_names: list[str] = self.provider_without_key.get_niches_names(categories[category_id].name,
                                                                                 niche_num)
            filtered_niches_names: list[str] = self.niche_service.filter_existing_names(niches_names, category_id)
            niches: list[Niche] = self.provider_without_key.get_niches(filtered_niches_names)
            self.niche_service.create_all(niches, category_id)

    def fill_niche_by_name(self, niche_name: str, product_num: int = -1) -> Niche | None:
        if not self.category_service.exists_with_name(DEFAULT_CATEGORY_NAME, self.marketplace_id):
            self.category_service.create(Category(DEFAULT_CATEGORY_NAME), self.marketplace_id)
        default_category_search_result = \
            self.category_service.find_by_name(DEFAULT_CATEGORY_NAME, self.marketplace_id)
        _, default_category_id = default_category_search_result
        niches: list[Niche] = self.provider_without_key.get_niches([niche_name])
        loaded_niche = niches[0]
        loaded_products = self.__get_new_products(niche_name, DEFAULT_CATEGORY_NAME, product_num)
        loaded_niche.products = loaded_products
        self.niche_service.create(loaded_niche, default_category_id)
        _, loaded_niche_id = self.niche_service.find_by_name(loaded_niche.name, default_category_id)
        self.__check_warehouse_filled(loaded_niche.products)
        self.product_service.create_products(loaded_niche.products, loaded_niche_id)
        return loaded_niche

    def __check_warehouse_filled(self, products: list[Product]):
        warehouse_ids: set[int] = set()
        for product in products:
            for history_unit in product.history.get_history():
                for warehouse_id in history_unit.leftover:
                    warehouse_ids.add(warehouse_id)
        filtered_warehouse_global_ids = self.warehouse_service.fileter_existing_global_ids(warehouse_ids)
        warehouse_to_add_as_unfilled: list[Warehouse] = []
        for global_id in filtered_warehouse_global_ids:
            warehouse_to_add_as_unfilled.append(self.__create_warehouse_with_global_id(global_id))
        self.__fill_warehouses(warehouse_to_add_as_unfilled)

    @staticmethod
    def __create_warehouse_with_global_id(global_id: int) -> Warehouse:
        return Warehouse(  # TODO think about loading ALL warehouses from WB
            f"unfilled{global_id}",
            global_id,
            HandlerType.MARKETPLACE,
            Address(),
            basic_logistic_to_customer_commission=0,
            additional_logistic_to_customer_commission=0,
            logistic_from_customer_commission=0,
            basic_storage_commission=0,
            additional_storage_commission=0,
            mono_palette_storage_commission=0
        )

    def __fill_warehouses(self, warehouses: list[Warehouse]):
        for warehouse in warehouses:
            self.warehouse_service.create_warehouse(warehouse, self.marketplace_id)

    def fill_products(self, products_per_niche: int = -1):
        categories: dict[int, Category] = self.category_service.find_all_in_marketplace(self.marketplace_id)
        for category_id in categories:
            if categories[category_id].name == DEFAULT_CATEGORY_NAME:
                continue
            niche_dict = self.niche_service.find_all_in_category(category_id)
            for niche_id in niche_dict:
                products_to_add = self.__get_new_products(niche_dict[niche_id].name,
                                                          categories[category_id].name, products_per_niche, niche_id)
                self.product_service.create_products(products_to_add, niche_id)

    def __get_new_products(self, niche_name: str, category_name: str,
                           product_number: int = -1, niche_id: int = -1) -> list[Product]:
        products_info: set[ProductInfo] = \
            self.provider_without_key.get_products_mapped_info(niche_name, product_number)
        mapped_products_info = {product_info.global_id: product_info for product_info in products_info}
        filtered_id_name_cost = self.__filter_product_ids(mapped_products_info, niche_id)
        return self.provider_without_key.get_products(niche_name, category_name, filtered_id_name_cost)

    def __filter_product_ids(self,
                             mapped_products_info: dict[int, ProductInfo],
                             niche_id: int = -1) -> list[ProductInfo]:
        filtered_products_global_ids = list(mapped_products_info.keys())
        if niche_id != -1:
            filtered_products_global_ids: list[int] = \
                self.product_service.filter_existing_global_ids(niche_id, filtered_products_global_ids)
        return [
            mapped_products_info[global_id]
            for global_id in filtered_products_global_ids
        ]


class WildberriesDBFillerWithKeyImpl(WildberriesDBFillerWithKey):
    def __init__(self, session: Session,
                 provider_with_key: WildberriesUserMarketDataProvider,
                 db_initializer_class: Type[DBFillerInitializer]):
        super().__init__(session, provider_with_key, db_initializer_class)

    def fill_warehouse(self):
        warehouses: list[Warehouse] = self.provider_with_key.get_warehouses()
        self.warehouse_service.create_all(warehouses, self.marketplace_id)
