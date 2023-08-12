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
        categories_names: list[str] = data_provider_without_key.get_categories_names()
        filtered_categories_names: list[str] = self.category_service.filter_existing_names(categories_names,
                                                                                           marketplace_id)
        filtered_categories: list[Category] = data_provider_without_key.get_categories(filtered_categories_names)
        self.category_service.create_all(filtered_categories, marketplace_id)
        all_categories = data_provider_without_key.get_categories(categories_names)
        for category in all_categories:
            category_id: int = self.category_service.find_by_name(category.name, marketplace_id)[1]
            self.category_service.update(category_id, category)

    def update_all_niches(self, category_id: int, marketplace_id: int) -> None:
        data_provider_without_key: DataProviderWithoutKey = self.__create_data_provider_without_key(marketplace_id)
        categories = self.category_service.find_all_in_marketplace(marketplace_id)
        niches_names: list[str] = data_provider_without_key.get_niches_names(categories[category_id].name)
        filtered_niches_names: list[str] = self.niche_service.filter_existing_names(niches_names, category_id)
        filtered_niches: list[Niche] = data_provider_without_key.get_niches(filtered_niches_names)
        self.niche_service.create_all(filtered_niches, category_id)
        all_niches_in_category: list[Niche] = data_provider_without_key.get_niches(niches_names)
        for niche in all_niches_in_category:
            niche_id: int = self.niche_service.find_by_name(niche.name, category_id)[1]
            self.niche_service.update(niche_id, niche)

    # TODO return Niche|None (Function fetch_by_id_atomic returned Niche or None)?
    def update_niche(self, niche_id: int, category_id: int, marketplace_id: int) -> Niche:
        data_provider_without_key: DataProviderWithoutKey = self.__create_data_provider_without_key(marketplace_id)
        niche_name_from_db: str = self.niche_service.fetch_by_id_atomic(niche_id).name
        new_data_from_niche: Niche = data_provider_without_key.get_niche(niche_name_from_db)
        self.niche_service.update(niche_id, new_data_from_niche)
        return new_data_from_niche

    def update_product(self, product_id: int, marketplace_id: int) -> Product:
        data_provider_without_key: DataProviderWithoutKey = self.__create_data_provider_without_key(marketplace_id)
        product_from_db: Product = self.product_card_service.find_by_id(product_id)
        product: Product = \
            data_provider_without_key.get_products(product_from_db.niche_name, product_from_db.category_name,
                                                   [product_from_db.global_id])[0]
        self.product_card_service.update(product_id, product)
        return product

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
        products: list[Product] = []
        for category_name in category_niche_dict:
            category_id: int = self.category_service.find_by_name(category_name, marketplace_id)[1]
            if category_id is None:
                self.update_all_categories(marketplace_id)
            for niche_name in category_niche_dict[category_name]:
                products.extend(data_provider_without_key.get_products(niche_name, category_name,
                                                                       category_niche_dict[category_name][niche_name]))
                niche_id_by_name: int = self.niche_service.find_by_name(niche_name, category_id)[1]
                if niche_id_by_name is None:
                    self.load_new_niche(niche_name, marketplace_id)

                filtered_products_ids = self.product_card_service.filter_existing_global_ids(niche_id_by_name,
                                                                                             category_niche_dict[
                                                                                                 category_name][
                                                                                                 niche_name])
                if filtered_products_ids is not None:
                    products_filtered = data_provider_without_key.get_products(niche_name, category_name,
                                                                               filtered_products_ids)
                    self.product_card_service.create_products(products_filtered, niche_id_by_name)
                products_ids = self.product_card_service.find_all_in_niche(niche_id_by_name)
                for product_id in products_ids:
                    user_products = self.user_item_service.fetch_user_products(user_id, marketplace_id)
                    if product_id not in user_products:
                        self.user_item_service.append_product(user_id, product_id)

        return products

    @staticmethod
    def __get_mapping_category_and_niche_names(products_global_ids: list[int],
                                               data_provider_without_key: DataProviderWithoutKey):
        category_niche_dict: dict[str, dict[str, list[int]]] = {}
        for product_global_id in products_global_ids:
            category_name: [str, str] = data_provider_without_key.get_category_and_niche(product_global_id)
            if category_name[0] not in category_niche_dict:
                category_niche_dict[category_name[0]] = {}
            niche_dict = category_niche_dict[category_name[0]]
            if category_name[1] not in niche_dict:
                niche_dict[category_name[1]] = []
            niche_dict[category_name[1]].append(product_global_id)
        return category_niche_dict

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
