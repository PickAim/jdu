from typing import Type

from jarvis_db.services.market.infrastructure.marketplace_service import MarketplaceService
from jarvis_db.services.market.person import UserService
from jarvis_db.services.market.service.economy_service import EconomyService
from jarvis_db.services.market.service.frequency_service import FrequencyService
from jorm.jarvis.db_update import JORMChanger
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

from jdu.db_tools.fill.db_fillers import StandardDBFiller
from jdu.providers.initializers import DataProviderInitializer
from jdu.providers.providers import UserMarketDataProvider


class JORMChangerImpl(JORMChanger):

    def __init__(
            self,
            economy_service: EconomyService,
            frequency_service: FrequencyService,
            user_service: UserService,
            marketplace_service: MarketplaceService,
            db_filler: StandardDBFiller,
            provider_initializing_mapping: dict[str, tuple[Type[UserMarketDataProvider], Type[DataProviderInitializer]]]
    ):
        self.__economy_service = economy_service
        self.__frequency_service = frequency_service
        self.__db_filler = db_filler
        self.__user_service = user_service
        self.__marketplace_service = marketplace_service
        self.__provider_initializing_mapping = provider_initializing_mapping

    def save_unit_economy_request(self, request: UnitEconomyRequest, result: UnitEconomyResult,
                                  request_info: RequestInfo, user_id: int) -> int:
        return self.__economy_service.save_request(request_info, request, result, user_id)

    def save_frequency_request(
            self,
            request: FrequencyRequest,
            result: FrequencyResult,
            request_info: RequestInfo,
            user_id: int,
    ) -> int:
        return self.__frequency_service.save(request_info, request, result, user_id)

    # TODO implement us
    def update_all_categories(self, marketplace_id: int) -> None:
        pass

    def update_all_niches(self, category_id: int) -> None:
        pass

    def update_niche(self, niche_id: int) -> Niche:
        pass

    def update_product(self, product_id: int) -> Product:
        pass

    def delete_unit_economy_request(self, request_id: int, user_id: int) -> None:
        self.__economy_service.remove(request_id)

    def delete_frequency_request(self, request_id: int, user_id: int) -> None:
        self.__frequency_service.remove(request_id)

    def load_new_niche(self, niche_name: str) -> Niche:
        return self.__db_filler.fill_niche_by_name(niche_name)

    def load_user_products(self, user_id: int, marketplace_id: int) -> list[Product]:
        # TODO implement me
        return [Product("product1", 1000, 124568, 4.0, "brand1", "seller", "niche1", "category1"),
                Product("product2", 105240, 987654, 2.3, "brand2", "seller", "niche2", "category2")]

    def load_user_warehouse(self, user_id: int, marketplace_id: int) -> list[Warehouse]:
        user_market_data_provider: UserMarketDataProvider = self.__create_user_market_data_provider(user_id,
                                                                                                    marketplace_id)
        if user_market_data_provider is None:
            return []
        return self.__db_filler.fill_warehouse(user_market_data_provider)

    def __create_user_market_data_provider(self, user_id: int, marketplace_id: int) -> UserMarketDataProvider | None:
        user: User = self.__user_service.find_by_id(user_id)
        if marketplace_id not in user.marketplace_keys:
            return None
        marketplace_api_key = user.marketplace_keys[marketplace_id]
        initializer_info = self.__map_marketplace_to_provider_initializer(marketplace_id=marketplace_id)
        if initializer_info is None:
            return None
        user_market_data_provider_class = initializer_info[0]
        initializer = initializer_info[1]
        return user_market_data_provider_class(api_key=marketplace_api_key, data_provider_initializer_class=initializer)

    def __map_marketplace_to_provider_initializer(self, marketplace_id: int) \
            -> tuple[Type[UserMarketDataProvider], Type[DataProviderInitializer]] | None:
        id_to_marketplace = self.__marketplace_service.find_all()
        if marketplace_id not in id_to_marketplace:
            return None
        marketplace_name = id_to_marketplace[marketplace_id].name
        if marketplace_name not in self.__provider_initializing_mapping:
            return None
        return self.__provider_initializing_mapping[marketplace_name]
