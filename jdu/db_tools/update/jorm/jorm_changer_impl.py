from typing import Type, Callable

from jorm.market.infrastructure import Niche, Warehouse, Category
from jorm.market.items import Product, ProductHistory
from jorm.market.person import User
from jorm.market.service import (
    FrequencyRequest,
    FrequencyResult,
    RequestInfo,
    UnitEconomyRequest,
    UnitEconomyResult,
)
from jorm.server.providers.providers import DataProviderWithoutKey, UserMarketDataProvider
from sqlalchemy.orm import Session

from jdu.db_tools.fill.db_fillers import StandardDBFiller
from jdu.db_tools.update.jorm.base import JORMChangerBase, InitInfo
from jdu.db_tools.update.jorm.initializers import JORMChangerInitializer
from jdu.support.utils import map_to_dict


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

    # def update_all_niches(self, category_id: int, marketplace_id: int) -> None:
    #     # TODO it will be necessary to implement this method to update niche commissions as example
    #     https://github.com/PickAim/jdu/issues/55
    #     return

    def update_niche(self, niche_id: int, category_id: int, marketplace_id: int) -> Niche | None:
        data_provider_without_key: DataProviderWithoutKey = self.__create_data_provider_without_key(marketplace_id)
        if data_provider_without_key is None:
            return None
        found_info: Niche = self.niche_service.find_by_id(niche_id)
        if found_info is None:
            return None
        niche = found_info
        found_info: Category = self.category_service.find_by_id(category_id)
        if found_info is None:
            return None
        category = found_info
        found_info: tuple[Niche, int] = self.niche_service.find_by_name_atomic(niche.name, category_id)
        if found_info is None:
            return None
        niche, _ = found_info
        return self.__update_niche((niche, niche_id), category, data_provider_without_key)

    def __update_niche(self, niche_info: tuple[Niche, int], category: Category,
                       data_provider_without_key: DataProviderWithoutKey) -> Niche:
        niche, niche_id = niche_info
        all_products_ids = data_provider_without_key.get_products_globals_ids(niche.name)
        new_products = data_provider_without_key.get_products(niche.name, category.name, all_products_ids)
        to_create, to_update = self.__split_products_to_create_and_update(niche.products, new_products)
        self.product_card_service.create_products(to_create, niche_id)
        for product in to_update:
            _, product_id = self.product_card_service.find_by_global_id(product.global_id, niche_id)
            self.product_card_service.update(product_id, product)
            self.product_history_service.create(product.history, product_id)
        all_updated_products = [*to_update, *to_create]
        niche.products = all_updated_products
        return niche

    def __split_products_to_create_and_update(self,
                                              existing_products: list[Product],
                                              new_products: list[Product]) -> tuple[list[Product], list[Product]]:
        get_global_id: Callable[[Product], int] = lambda product: product.global_id
        get_product: Callable[[Product], Product] = lambda product: product
        global_id_to_existing_product = map_to_dict(get_global_id, get_product, existing_products)
        global_id_to_new_product = map_to_dict(get_global_id, get_product, new_products)
        to_create: list[Product] = []
        to_update: list[Product] = []
        for global_id in global_id_to_new_product:
            if global_id in global_id_to_existing_product:
                product_to_update = self.__merge_products(global_id_to_existing_product[global_id],
                                                          global_id_to_new_product[global_id])
                to_update.append(product_to_update)
            else:
                to_create.append(global_id_to_new_product[global_id])
        return to_create, to_update

    def __merge_products(self, into: Product, new_product: Product) -> Product:
        new_history = new_product.history.get_history()
        if len(new_history) > 0:
            into.history = self.__extract_only_new_histories(into.history, new_product.history)
        into.name = new_product.name
        into.width = new_product.width
        into.height = new_product.height
        into.depth = new_product.depth
        into.cost = new_product.cost
        into.brand = new_product.brand
        into.seller = new_product.seller
        into.rating = new_product.rating
        return into

    @staticmethod
    def __extract_only_new_histories(old_history: ProductHistory, new_history: ProductHistory) -> ProductHistory:
        old_units = old_history.get_history()
        new_units = new_history.get_history()
        existing_dates = {unit.unit_date for unit in old_units}
        result_units = []
        for unit in new_units:
            if unit.unit_date not in existing_dates:
                result_units.append(unit)
        return ProductHistory(result_units)

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

    def load_user_products(self, user_id: int, marketplace_id: int) -> list[Product] | None:
        user_market_data_provider: UserMarketDataProvider = self.__create_user_market_data_provider(user_id,
                                                                                                    marketplace_id)
        data_provider_without_key: DataProviderWithoutKey = self.__create_data_provider_without_key(marketplace_id)
        if user_market_data_provider is None or data_provider_without_key is None:
            return None
        user_products = self.__get_user_products(user_market_data_provider, data_provider_without_key)
        user_products_in_db = self.user_item_service.fetch_user_products(user_id, marketplace_id)
        existing_products = [
            user_products_in_db[product_id] for product_id in user_products_in_db
        ]
        user_products = self.__create_and_update_user_products(user_id, existing_products,
                                                               user_products, marketplace_id)
        return user_products

    def __create_and_update_user_products(self, user_id: int,
                                          existing_products: list[Product],
                                          new_products: list[Product], marketplace_id: int) -> list[Product]:
        to_create, to_update = self.__split_products_to_create_and_update(existing_products, new_products)
        for product in to_create:
            found_info = self.category_service.find_by_name(product.category_name, marketplace_id)
            if found_info is None:
                continue
            category_id: int = found_info[1]
            found_info = self.niche_service.find_by_name(product.niche_name, category_id)
            if found_info is None:
                continue
            niche_id: int = found_info[1]
            product_id = self.product_card_service.create_product(product, niche_id)
            self.user_item_service.append_product(user_id, product_id)
        for product in to_update:
            found_info = self.category_service.find_by_name(product.category_name, marketplace_id)
            if found_info is None:
                continue
            category_id: int = found_info[1]
            found_info = self.niche_service.find_by_name(product.niche_name, category_id)
            if found_info is None:
                continue
            niche_id: int = found_info[1]
            found_info = self.product_card_service.find_by_global_id(product.global_id, niche_id)
            if found_info is None:
                continue
            product_id = found_info[1]
            self.product_card_service.update(product_id, product)
            self.user_item_service.append_product(user_id, product_id)
        return [*to_create, *to_update]

    def __get_user_products(self,
                            user_market_data_provider: UserMarketDataProvider,
                            data_provider_without_key: DataProviderWithoutKey) -> list[Product]:
        products_global_ids: list[int] = user_market_data_provider.get_user_products()
        base_products = data_provider_without_key.get_base_products(products_global_ids)
        products_id_to_cat_niche_name = self.__get_products_category_and_niche([
            product.global_id for product in base_products
        ], data_provider_without_key)
        for product in base_products:
            if product.global_id in products_id_to_cat_niche_name:
                category_and_niche = products_id_to_cat_niche_name[product.global_id]
                product.category_name = category_and_niche[0]
                product.niche_name = category_and_niche[1]
        return base_products

    @staticmethod
    def __get_products_category_and_niche(products_ids: list[int],
                                          data_provider_without_key: DataProviderWithoutKey) \
            -> dict[int, tuple[str, str]]:
        result: dict[int, tuple[str, str]] = {}
        for product_id in products_ids:
            category_and_niche = data_provider_without_key.get_category_and_niche(product_id)
            if category_and_niche is None:
                continue
            result[product_id] = category_and_niche
        return result

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
