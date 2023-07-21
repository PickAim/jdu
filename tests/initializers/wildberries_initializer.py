from jarvis_db.factories.services import create_marketplace_service, create_category_service, create_niche_service, \
    create_warehouse_service, create_product_history_service, create_product_card_service
import requests
from jarvis_db.repositores.mappers.market.infrastructure import NicheTableToJormMapper, MarketplaceTableToJormMapper, \
    WarehouseTableToJormMapper, CategoryTableToJormMapper
from jarvis_db.repositores.mappers.market.items import ProductTableToJormMapper, ProductHistoryTableToJormMapper
from jarvis_db.repositores.mappers.market.items.leftover_mappers import LeftoverTableToJormMapper
from jarvis_db.repositores.market.infrastructure import WarehouseRepository, MarketplaceRepository, \
    CategoryRepository, NicheRepository
from jarvis_db.repositores.market.items import ProductHistoryRepository, ProductCardRepository
from jarvis_db.repositores.market.items.leftover_repository import LeftoverRepository
from jarvis_db.services.market.infrastructure.category_service import CategoryService
from jarvis_db.services.market.infrastructure.marketplace_service import MarketplaceService
from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.services.market.infrastructure.warehouse_service import WarehouseService
from jarvis_db.services.market.items.leftover_service import LeftoverService
from jarvis_db.services.market.items.product_card_service import ProductCardService
from jarvis_db.services.market.items.product_history_service import ProductHistoryService
from jarvis_db.services.market.items.product_history_unit_service import ProductHistoryUnitService
from requests.adapters import HTTPAdapter
# from requests.adapters import HTTPAdapter
from sqlalchemy.orm import Session

from jdu.db_tools.fill.base import DBFiller
from jdu.db_tools.fill.initializers import DBFillerInitializer
from jdu.providers.initializers_provider import DataProviderInitializer
from jdu.support.commission.wildberries_commission_resolver import WildberriesCommissionResolver


class WildberriesTestDataProviderInitializer(DataProviderInitializer):
    def additional_data_provider(self, data_provider):
        data_provider.commission_resolver = WildberriesCommissionResolver()
        data_provider.session = requests.Session()
        __adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100)
        data_provider.session.mount('https://', __adapter)


class WildberriesTestDBFillerInitializer(DBFillerInitializer):
    WILDBERRIES_NAME = 'wildberries'

    def get_marketplace_name(self) -> str:
        return self.WILDBERRIES_NAME

    def additional_init_db_filler(self, session: Session, db_filler: DBFiller):
        db_filler.marketplace_service = create_marketplace_service(session)
        db_filler.category_service = create_category_service(session)
        db_filler.niche_service = create_niche_service(session)

        db_filler.product_service = create_product_card_service(session)
        db_filler.warehouse_service = create_warehouse_service(session)
        db_filler.product_history_service = create_product_history_service(session)
