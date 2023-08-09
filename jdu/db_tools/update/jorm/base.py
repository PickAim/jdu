from abc import ABC
from dataclasses import dataclass
from typing import Type

from jarvis_db.services.market.infrastructure.category_service import CategoryService
from jarvis_db.services.market.infrastructure.marketplace_service import MarketplaceService
from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.services.market.infrastructure.warehouse_service import WarehouseService
from jarvis_db.services.market.items.product_card_service import ProductCardService
from jarvis_db.services.market.person import UserService
from jarvis_db.services.market.service.economy_service import EconomyService
from jarvis_db.services.market.service.frequency_service import FrequencyService
from jorm.jarvis.db_update import JORMChanger
from jorm.jarvis.initialization import Initializable

from jdu.db_tools.fill.db_fillers import StandardDBFiller
from jdu.db_tools.fill.initializers import DBFillerInitializer
from jdu.providers.initializers import DataProviderInitializer
from jdu.providers.providers import UserMarketDataProvider, DataProviderWithoutKey


@dataclass
class InitInfo:
    user_market_data_provider_class: Type[UserMarketDataProvider]
    data_provider_without_key_class: Type[DataProviderWithoutKey]
    db_filler_class: Type[StandardDBFiller]

    data_provider_initializer_class: Type[DataProviderInitializer]
    db_filler_initializer_class: Type[DBFillerInitializer]


class JORMChangerBase(JORMChanger, Initializable, ABC):
    def __init__(self):
        self.economy_service: EconomyService | None = None
        self.frequency_service: FrequencyService | None = None
        self.user_service: UserService | None = None
        self.marketplace_service: MarketplaceService | None = None
        self.warehouse_service: WarehouseService | None = None
        self.category_service: CategoryService | None = None
        self.niche_service: NicheService | None = None
        self.product_card_service: ProductCardService | None = None
        self.initializing_mapping: dict[str, InitInfo] = {}
