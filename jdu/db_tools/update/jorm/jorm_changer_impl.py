from typing import Type

from jorm.market.infrastructure import Niche, Warehouse, Category
from jorm.market.items import Product
from jorm.market.person import User
from jorm.market.service import (
    FrequencyRequest,
    FrequencyResult,
    RequestInfo,
    UnitEconomyRequest,
    UnitEconomyResult,
)
from sqlalchemy.orm import Session

from jdu.db_tools.fill.db_fillers import StandardDBFiller
from jdu.db_tools.update.jorm.base import JORMChangerBase, InitInfo
from jdu.db_tools.update.jorm.initializers import JORMChangerInitializer
from jdu.providers.providers import UserMarketDataProvider, DataProviderWithoutKey


class JORMChangerImpl(JORMChangerBase):
    def __init__(self, session: Session, initializer_class: Type[JORMChangerInitializer]):
        super().__init__()
        initializer_class(session).init_object(self)

    def save_unit_economy_request(self, request: UnitEconomyRequest, result: UnitEconomyResult,
                                  request_info: RequestInfo, user_id: int) -> int:
        return self.economy_service.save_request(request_info, request, result, user_id)

    def save_frequency_request(
            self,
            request: FrequencyRequest,
            result: FrequencyResult,
            request_info: RequestInfo,
            user_id: int,
    ) -> int:
        return self.frequency_service.save(request_info, request, result, user_id)

    def update_all_categories(self, marketplace_id: int) -> None:
        data_provider_without_key: DataProviderWithoutKey = self.__create_data_provider_without_key(marketplace_id)
        if data_provider_without_key is None:
            return
        categories_names: list[str] = data_provider_without_key.get_categories_names()
        filtered_categories_names: list[str] = self.category_service.filter_existing_names(categories_names,
                                                                                           marketplace_id)
        filtered_categories: list[Category] = data_provider_without_key.get_categories(filtered_categories_names)
        self.category_service.create_all(filtered_categories, marketplace_id)

    def update_all_niches(self, category_id: int, marketplace_id: int) -> None:
        data_provider_without_key: DataProviderWithoutKey = self.__create_data_provider_without_key(marketplace_id)
        found_category = self.category_service.find_by_id(category_id)
        if found_category is None or data_provider_without_key is None:
            return
        niches_names: list[str] = data_provider_without_key.get_niches_names(found_category.name)
        filtered_niches_names: list[str] = self.niche_service.filter_existing_names(niches_names, category_id)
        filtered_niches: list[Niche] = data_provider_without_key.get_niches(filtered_niches_names)
        self.niche_service.create_all(filtered_niches, category_id)
        all_niches_in_category: list[Niche] = data_provider_without_key.get_niches(
            list(set(niches_names) - set(filtered_niches_names)))
        for niche in all_niches_in_category:
            found_niche_info: tuple[Niche, int] = self.niche_service.find_by_name(niche.name, category_id)
            if found_niche_info is None:
                continue
            products = self.__update_or_create_products_by_niche(data_provider_without_key, found_niche_info[1],
                                                                 found_category.name, marketplace_id)
            if products is None:
                return None

    def update_niche(self, niche_id: int, category_id: int, marketplace_id: int) -> Niche | None:
        data_provider_without_key: DataProviderWithoutKey = self.__create_data_provider_without_key(marketplace_id)
        found_niche: Niche = self.niche_service.find_by_id(niche_id)
        found_category = self.category_service.find_by_id(category_id)
        if found_niche is None or found_category is None or data_provider_without_key is None:
            return None
        products = self.__update_or_create_products_by_niche(data_provider_without_key, niche_id,
                                                             found_category.name, marketplace_id)
        if products is None:
            return None
        
        return found_niche

    def update_product(self, product_id: int, marketplace_id: int) -> Product | None:
        data_provider_without_key: DataProviderWithoutKey = self.__create_data_provider_without_key(marketplace_id)
        product_from_db: Product = self.product_card_service.find_by_id(product_id)
        if product_from_db is None:
            return None
        niche_name = product_from_db.niche_name
        category_name = product_from_db.category_name
        found_category_info = self.category_service.find_by_name(category_name, marketplace_id)
        if data_provider_without_key is None or found_category_info is None:
            return None

        found_info_niche: tuple[Niche, int] = self.niche_service.find_by_name(niche_name, found_category_info[1])
        if found_info_niche is None:
            return None
        products = self.__update_or_create_products_by_niche(data_provider_without_key, found_info_niche[1],
                                                             category_name, marketplace_id,
                                                             [product_from_db.global_id])
        if len(products) == 0:
            return None
        return products[0]

    def delete_unit_economy_request(self, request_id: int, user_id: int) -> None:
        self.economy_service.remove(request_id)

    def delete_frequency_request(self, request_id: int, user_id: int) -> None:
        self.frequency_service.remove(request_id)

    def load_new_niche(self, niche_name: str, marketplace_id: int) -> Niche | None:
        data_provider_without_key = self.__create_data_provider_without_key(marketplace_id)
        db_filler = self.__create_standard_db_filler(marketplace_id)
        if data_provider_without_key is None or db_filler is None:
            return None
        return db_filler.fill_niche_by_name(self.category_service, self.niche_service,
                                            self.product_card_service, data_provider_without_key, niche_name)

    def load_user_products(self, user_id: int, marketplace_id: int) -> list[Product]:
        user_market_data_provider: UserMarketDataProvider = self.__create_user_market_data_provider(user_id,
                                                                                                    marketplace_id)
        data_provider_without_key: DataProviderWithoutKey = self.__create_data_provider_without_key(marketplace_id)
        if user_market_data_provider is None or data_provider_without_key is None:
            return []
        products_global_ids: list[int] = user_market_data_provider.get_user_products()
        category_niche_dict: dict[str, dict[str, list[int]]] = self.__get_mapping_category_and_niche_names(
            products_global_ids, data_provider_without_key)
        products: list[Product] = self.__create_or_update_user_products(data_provider_without_key, category_niche_dict,
                                                                        marketplace_id, user_id)
        return products

    def load_user_warehouse(self, user_id: int, marketplace_id: int) -> list[Warehouse]:
        user_market_data_provider: UserMarketDataProvider = self.__create_user_market_data_provider(user_id,
                                                                                                    marketplace_id)
        db_filler = self.__create_standard_db_filler(marketplace_id)
        if user_market_data_provider is None or db_filler is None:
            return []
        return db_filler.fill_warehouse(user_market_data_provider)

    def __create_standard_db_filler(self, marketplace_id: int) -> StandardDBFiller | None:
        init_info = self.__map_marketplace_to_init_info(marketplace_id=marketplace_id)
        if init_info is None:
            return None
        initializer_class = init_info.db_filler_initializer_class
        db_filler_class = init_info.db_filler_class
        return db_filler_class(marketplace_service=self.marketplace_service,
                               warehouse_service=self.warehouse_service, db_initializer_class=initializer_class)

    def __create_data_provider_without_key(self, marketplace_id: int) -> DataProviderWithoutKey | None:
        init_info = self.__map_marketplace_to_init_info(marketplace_id=marketplace_id)
        if init_info is None:
            return None
        data_provider_without_key_class = init_info.data_provider_without_key_class
        initializer_class = init_info.data_provider_initializer_class
        return data_provider_without_key_class(data_provider_initializer_class=initializer_class)

    def __create_user_market_data_provider(self, user_id: int, marketplace_id: int) -> UserMarketDataProvider | None:
        init_info = self.__map_marketplace_to_init_info(marketplace_id=marketplace_id)
        if init_info is None:
            return None
        user: User = self.user_service.find_by_id(user_id)
        if user is None or marketplace_id not in user.marketplace_keys:
            return None
        marketplace_api_key = user.marketplace_keys[marketplace_id]
        user_market_data_provider_class = init_info.user_market_data_provider_class
        initializer_class = init_info.data_provider_initializer_class
        return user_market_data_provider_class(api_key=marketplace_api_key,
                                               data_provider_initializer_class=initializer_class)

    def __map_marketplace_to_init_info(self, marketplace_id: int) \
            -> InitInfo | None:
        id_to_marketplace = self.marketplace_service.find_all()
        if marketplace_id not in id_to_marketplace:
            return None
        marketplace_name = id_to_marketplace[marketplace_id].name
        if marketplace_name not in self.initializing_mapping:
            return None
        return self.initializing_mapping[marketplace_name]

    def __update_or_create_products_by_niche(self, data_provider_without_key: DataProviderWithoutKey,
                                             niche_id: int, category_name: str, marketplace_id: int,
                                             products_global_ids: list[int] = None) -> \
            list[Product] | None:
        niche = self.niche_service.find_by_id(niche_id)
        if niche is None:
            return []
        if products_global_ids is None:
            products_global_ids = data_provider_without_key.get_products_globals_ids(niche.name)

        filtering_global_ids: list[int] = self.product_card_service.filter_existing_global_ids(niche_id,
                                                                                               products_global_ids)
        filtering_products: list[Product] = data_provider_without_key.get_products(niche.name,
                                                                                   category_name,
                                                                                   filtering_global_ids)
        if len(filtering_products) != 0:
            self.product_card_service.create_products(filtering_products, niche_id)
        products = data_provider_without_key.get_products(niche.name, category_name, products_global_ids)
        products_list_without_filtering = [x for x in products if x not in filtering_products]
        for product in products_list_without_filtering:
            found_info_product = self.product_card_service.find_by_gloabal_id(product.global_id, marketplace_id)
            if found_info_product is None:
                return []

            self.product_card_service.update(found_info_product[1], product)
        return products

    @staticmethod
    def __get_mapping_category_and_niche_names(products_global_ids: list[int],
                                               data_provider_without_key: DataProviderWithoutKey):
        category_niche_dict: dict[str, dict[str, list[int]]] = {}
        for product_global_id in products_global_ids:
            category_niche_name: [str, str] = data_provider_without_key.get_category_and_niche(product_global_id)
            if category_niche_name[0] not in category_niche_dict:
                category_niche_dict[category_niche_name[0]] = {}
            niche_dict = category_niche_dict[category_niche_name[0]]
            if category_niche_name[1] not in niche_dict:
                niche_dict[category_niche_name[1]] = []
            niche_dict[category_niche_name[1]].append(product_global_id)
        return category_niche_dict

    def __create_or_update_user_products(self, data_provider_without_key: DataProviderWithoutKey,
                                         category_niche_dict: dict[str, dict[str, list[int]]],
                                         marketplace_id: int, user_id) -> list[
        Product]:
        products: list[Product] = []
        for category_name in category_niche_dict:
            found_category_info: tuple[Category, int] = self.category_service.find_by_name(category_name,
                                                                                           marketplace_id)
            if found_category_info is None:
                categories = data_provider_without_key.get_categories([category_name])
                if len(categories) == 0:
                    continue

                self.category_service.create(categories[0], marketplace_id)
            found_category_info = self.category_service.find_by_name(category_name,
                                                                     marketplace_id)
            for niche_name in category_niche_dict[category_name]:
                products.extend(data_provider_without_key.get_products(niche_name, category_name,
                                                                       category_niche_dict[category_name][niche_name]))
                found_niche_info: tuple[Niche, int] = self.niche_service.find_by_name(niche_name,
                                                                                      found_category_info[1])
                if found_niche_info is None:
                    self.load_new_niche(niche_name, marketplace_id)
                found_niche_info: tuple[Niche, int] = self.niche_service.find_by_name(niche_name,
                                                                                      found_category_info[1])
                filtered_products_ids = self.product_card_service.filter_existing_global_ids(found_niche_info[1],
                                                                                             category_niche_dict[
                                                                                                 category_name][
                                                                                                 niche_name])
                if len(filtered_products_ids) != 0:
                    self.__update_or_create_products_by_niche(data_provider_without_key, found_niche_info[1],
                                                              category_name, marketplace_id,
                                                              filtered_products_ids)
                products_ids = self.product_card_service.find_all_in_niche(found_niche_info[1])
                user_products = self.user_item_service.fetch_user_products(user_id, marketplace_id)
                for product_id in products_ids:
                    if product_id not in user_products:
                        self.user_item_service.append_product(user_id, product_id)
        return products
