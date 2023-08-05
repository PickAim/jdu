from abc import ABC
from typing import Type

from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.items import Product
from jorm.market.person import User
from jorm.market.service import (
    FrequencyRequest,
    FrequencyResult,
    RequestInfo,
    UnitEconomyRequest,
    UnitEconomyResult,
)
from jorm.support.constants import DEFAULT_CATEGORY_NAME, DEFAULT_NICHE_NAME
from sqlalchemy.orm import Session

from jdu.db_tools.fill.db_fillers import StandardDBFiller
from jdu.db_tools.update.jorm.base import JORMChangerBase, InitInfo
from jdu.db_tools.update.jorm.initializers import JORMChangerInitializer
from jdu.providers.providers import UserMarketDataProvider, DataProviderWithoutKey


class __InitializableJORMChanger(JORMChangerBase, ABC):
    def __init__(self, session: Session, initializer_class: Type[JORMChangerInitializer]):
        super().__init__()
        initializer_class.init_jorm_changer(session, self)


class JORMChangerImpl(__InitializableJORMChanger):
    def __init__(self, session: Session, initializer_class: Type[JORMChangerInitializer]):
        super().__init__(session, initializer_class)

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

    # TODO implement us
    def update_all_categories(self, marketplace_id: int) -> None:
        categories = self.category_service.find_all_in_marketplace(marketplace_id)
        for category_id in categories:
            self.category_service.update(category_id, categories[category_id])

    def update_all_niches(self, category_id: int, marketplace_id: int) -> None:
        pass

    def update_niche(self, niche_id: int, category_id: int, marketplace_id: int) -> Niche:
        pass

    def update_product(self, product_id: int, marketplace_id: int) -> Product:
        pass

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
        data_provider_without_key = self.__create_data_provider_without_key(marketplace_id)
        products_ids: list[int] = user_market_data_provider.get_user_products()
        # TODO get_niches_category?
        # TODO product_id?
        products = data_provider_without_key.get_products(DEFAULT_NICHE_NAME, DEFAULT_CATEGORY_NAME, products_ids)
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
        if marketplace_id not in user.marketplace_keys:
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
