import unittest

from jarvis_db.repositores.mappers.market.items import ProductHistoryTableToJormMapper
from jarvis_db.repositores.mappers.market.items.leftover_mappers import LeftoverTableToJormMapper
from jarvis_db.repositores.market.infrastructure import WarehouseRepository
from jarvis_db.repositores.market.items import ProductHistoryRepository
from jarvis_db.repositores.market.items.leftover_repository import LeftoverRepository
from jarvis_db.services.market.items.leftover_service import LeftoverService
from jarvis_db.services.market.items.product_history_service import ProductHistoryService
from jarvis_db.services.market.items.product_history_unit_service import ProductHistoryUnitService
from jarvis_db.tables import Marketplace, Warehouse, Address, ProductCard, Niche, Category

from jdu.db_tools import WildberriesDBFillerImpl, \
    WildberriesDBFiller
from jdu.providers import WildBerriesDataProviderWithoutKey
from provider_for_test.test_provider import WildBerriesDataProviderWithoutKeyImplTest
from tests.db_context import DbContext


class PriceHistoryFillerTest(unittest.TestCase):

    def setUp(self):
        self.__db_context = DbContext()
        with self.__db_context.session() as session, session.begin():
            marketplace = Marketplace(name='wildberries')
            category = Category(name='Category_1', marketplace=marketplace)
            niche = Niche(
                name='Niche_1',
                marketplace_commission=1,
                partial_client_commission=1,
                client_commission=1,
                return_percent=1,
                category=category)
            product = ProductCard(
                name='Product_1', global_id=12, rating=12, cost=230, niche=niche)
            session.add(product)
            session.flush()
            self.__product_id = product.id
            address = Address(
                country='AS',
                region='QS',
                street='DD',
                number='HH',
                corpus='YU'
            )
            warehouse = Warehouse(
                owner=marketplace,
                global_id=200,
                type=0,
                name='qwerty',
                address=address,
                basic_logistic_to_customer_commission=0,
                additional_logistic_to_customer_commission=0,
                logistic_from_customer_commission=0,
                basic_storage_commission=0,
                additional_storage_commission=0,
                monopalette_storage_commission=0
            )
            session.add(warehouse)
            session.flush()
            self.__warehouse_id = warehouse.id
            self.__warehouse_gid = warehouse.global_id

    def test_fill_price_history(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImplTest()
        with self.__db_context.session() as session, session.begin():
            wildberries_object_filler: WildberriesDBFiller = WildberriesDBFillerImpl(object_provider, session)
            wildberries_object_filler.fill_price_history("Niche_1")
        with self.__db_context.session() as session:
            history_unit_service = ProductHistoryUnitService(ProductHistoryRepository(session))
            price_history_service = ProductHistoryService(history_unit_service, LeftoverService(
                LeftoverRepository(session), WarehouseRepository(session), history_unit_service),
                                                          ProductHistoryRepository(session),
                                                          ProductHistoryTableToJormMapper(
                                                              LeftoverTableToJormMapper()))
            db_price_history = price_history_service.find_product_history(1)
            print(db_price_history)
