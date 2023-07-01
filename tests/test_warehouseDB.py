import unittest

from jarvis_db.repositores.mappers.market.infrastructure import WarehouseTableToJormMapper
from jarvis_db.repositores.market.infrastructure import WarehouseRepository
from jarvis_db.services.market.infrastructure.warehouse_service import WarehouseService
from jarvis_db.tables import Marketplace

from jdu.db_tools.fill.db_fillers import WildberriesDBFillerWithKeyImpl, WildberriesDBFillerWithKey
from jdu.providers import WildBerriesDataProviderWithKey
from tests.db_context import DbContext
from tests.provider_for_test.test_provider import WildBerriesDataProviderStandardImplTest


class WarehouseFillerTest(unittest.TestCase):

    def setUp(self):
        self.__db_context = DbContext()
        with self.__db_context.session() as session, session.begin():
            marketplace = Marketplace(name='wildberries')
            session.add(marketplace)
            session.flush()
            self.__marketplace_id = marketplace.id

    def test_fill_warehouses(self):
        object_provider: WildBerriesDataProviderWithKey = WildBerriesDataProviderStandardImplTest()
        with self.__db_context.session() as session, session.begin():
            wildberries_object_filler: WildberriesDBFillerWithKey = WildberriesDBFillerWithKeyImpl(
                object_provider, session)
            wildberries_object_filler.fill_warehouse()
        with self.__db_context.session() as session:
            warehouse_service = WarehouseService(WarehouseRepository(session), WarehouseTableToJormMapper())
            db_warehouse = warehouse_service.find_all_warehouses()
            self.assertEqual(len(db_warehouse), 10)
