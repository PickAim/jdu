import pickle
from typing import Type, Iterable

from jarvis_db.services.market.infrastructure.category_service import CategoryService
from jarvis_db.services.market.infrastructure.marketplace_service import MarketplaceService
from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.services.market.infrastructure.warehouse_service import WarehouseService
from jarvis_db.services.market.items.product_card_service import ProductCardService
from jorm.market.infrastructure import Category, Niche, Warehouse, HandlerType, Address
from jorm.market.items import Product
from jorm.support.constants import DEFAULT_CATEGORY_NAME

from jdu.db_tools.fill.db_fillers import StandardDBFiller
from jdu.db_tools.fill.initializers import DBFillerInitializer
from jdu.providers.providers import UserMarketDataProvider, DataProviderWithoutKey
from jdu.support.constant import NICHE_TO_CATEGORY


class StandardDBFillerImpl(StandardDBFiller):
    def __init__(self, marketplace_service: MarketplaceService,
                 warehouse_service: WarehouseService, db_initializer_class: Type[DBFillerInitializer]):
        super().__init__(marketplace_service, warehouse_service, db_initializer_class)

    def fill_categories(self, category_service: CategoryService,
                        data_provider_without_key: DataProviderWithoutKey, category_num: int = -1):
        categories_names: list[str] = data_provider_without_key.get_categories_names(category_num)
        filtered_categories_names: list[str] = \
            category_service.filter_existing_names(categories_names, self.marketplace_id)
        categories: list[Category] = data_provider_without_key.get_categories(filtered_categories_names)
        category_service.create_all(categories, self.marketplace_id)

    def fill_niches(self,
                    category_service: CategoryService,
                    niche_service: NicheService,
                    data_provider_without_key: DataProviderWithoutKey, niche_num: int = -1):
        categories: dict[int, Category] = category_service.find_all_in_marketplace(self.marketplace_id)
        for category_id in categories:
            niches_names: list[str] = data_provider_without_key.get_niches_names(categories[category_id].name,
                                                                                 niche_num)
            filtered_niches_names: list[str] = niche_service.filter_existing_names(niches_names, category_id)
            niches: list[Niche] = data_provider_without_key.get_niches(filtered_niches_names)
            niche_service.create_all(niches, category_id)

    def fill_niche_by_name(self,
                           category_service: CategoryService,
                           niche_service: NicheService,
                           product_card_service: ProductCardService,
                           data_provider_without_key: DataProviderWithoutKey,
                           niche_name: str, product_num: int = -1) -> Niche | None:
        category_name = DEFAULT_CATEGORY_NAME
        with open(NICHE_TO_CATEGORY, 'rb') as file:
            niche_to_category = pickle.load(file)
            if niche_name in niche_to_category:
                category_name = niche_to_category[niche_name]
        if not category_service.exists_with_name(category_name, self.marketplace_id):
            category_service.create(Category(category_name), self.marketplace_id)
        category_search_result = \
            category_service.find_by_name(category_name, self.marketplace_id)
        _, category_id = category_search_result
        return self.__get_niche(category_id, niche_service,
                                product_card_service, data_provider_without_key, niche_name, product_num)

    def __get_niche(self,
                    category_id: int,
                    niche_service: NicheService,
                    product_card_service: ProductCardService,
                    data_provider_without_key: DataProviderWithoutKey,
                    niche_name: str, product_num: int = -1) -> Niche | None:
        niches: list[Niche] = data_provider_without_key.get_niches([niche_name])
        loaded_niche = niches[0]
        loaded_products = self.__get_new_products(product_card_service, data_provider_without_key,
                                                  niche_name, DEFAULT_CATEGORY_NAME, product_num)
        if len(loaded_products) == 0:
            return None
        loaded_niche.products = loaded_products
        niche_service.create(loaded_niche, category_id)
        _, loaded_niche_id = niche_service.find_by_name(loaded_niche.name, category_id)
        self.__check_warehouse_filled(loaded_niche.products)
        product_card_service.create_products(loaded_niche.products, loaded_niche_id)
        return loaded_niche

    def __get_new_products(self,
                           product_card_service: ProductCardService,
                           data_provider_without_key: DataProviderWithoutKey,
                           niche_name: str, category_name: str, product_number: int = -1, niche_id: int = -1) \
            -> list[Product]:
        products_global_ids: set[int] = \
            data_provider_without_key.get_products_globals_ids(niche_name, product_number)
        print(f"{len(products_global_ids)} products in {niche_name} niche")
        filtered_products_globals_ids = self.__filter_product_ids(product_card_service, products_global_ids, niche_id)
        return data_provider_without_key.get_products(niche_name, category_name, filtered_products_globals_ids)

    @staticmethod
    def __filter_product_ids(product_card_service: ProductCardService,
                             products_global_ids: Iterable[int],
                             niche_id: int = -1) -> list[int]:
        if niche_id != -1:
            return product_card_service.filter_existing_global_ids(niche_id, products_global_ids)
        return list(products_global_ids)

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

    def fill_warehouse(self, provider_with_key: UserMarketDataProvider) -> list[Warehouse]:
        warehouses: list[Warehouse] = provider_with_key.get_warehouses()
        self.warehouse_service.create_all(warehouses, self.marketplace_id)
        return warehouses
