from abc import ABC, abstractmethod

from jarvis_db.repositores.mappers.market.infrastructure import NicheTableToJormMapper, MarketplaceTableToJormMapper, \
    WarehouseTableToJormMapper, CategoryTableToJormMapper
from jarvis_db.repositores.mappers.market.items import ProductTableToJormMapper, ProductHistoryTableToJormMapper
from jarvis_db.repositores.mappers.market.items.leftover_mappers import LeftoverTableToJormMapper
from jarvis_db.repositores.market.infrastructure import WarehouseRepository, MarketplaceRepository, CategoryRepository, \
    NicheRepository
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
from sqlalchemy.orm import Session

from jdu.db_tools.fill.base import _DBFiller


class DBFillerInitializer(ABC):
    @staticmethod
    @abstractmethod
    def init_db_filler(session: Session, db_filler_to_init: _DBFiller):
        pass


class WildberriesDBFillerInitializer(DBFillerInitializer):
    @staticmethod
    def init_db_filler(session: Session, db_filler: _DBFiller):
        db_filler.marketplace_name = 'wildberries'
        niche_table_to_jorm_mapper = NicheTableToJormMapper()
        product_history_repository = ProductHistoryRepository(session)
        warehouse_repository = WarehouseRepository(session)

        db_filler.marketplace_service = \
            MarketplaceService(MarketplaceRepository(session),
                               MarketplaceTableToJormMapper(WarehouseTableToJormMapper()))
        db_filler.category_service = CategoryService(CategoryRepository(session),
                                                     CategoryTableToJormMapper(niche_table_to_jorm_mapper))
        db_filler.niche_service = NicheService(NicheRepository(session), niche_table_to_jorm_mapper)
        db_filler.product_service = ProductCardService(ProductCardRepository(session),
                                                       ProductTableToJormMapper())
        db_filler.history_unit_service = ProductHistoryUnitService(product_history_repository)
        db_filler.warehouse_service = WarehouseService(warehouse_repository,
                                                       WarehouseTableToJormMapper())
        db_filler.product_history_service = \
            ProductHistoryService(db_filler.history_unit_service,
                                  LeftoverService(LeftoverRepository(session),
                                                  warehouse_repository,
                                                  db_filler.history_unit_service),
                                  product_history_repository,
                                  ProductHistoryTableToJormMapper(LeftoverTableToJormMapper()))
