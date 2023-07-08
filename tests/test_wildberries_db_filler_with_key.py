from jarvis_db.repositores.mappers.market.infrastructure import WarehouseTableToJormMapper
from jarvis_db.repositores.market.infrastructure import WarehouseRepository
from jarvis_db.services.market.infrastructure.warehouse_service import WarehouseService

from jdu.db_tools.fill.wildberries_fillers import WildberriesDBFillerWithKeyImpl, WildberriesDBFillerWithKey
from jdu.providers.wildberries_providers import WildberriesUserMarketDataProvider
from tests.basic_db_test import BasicDBTest, TestDBContextAdditions
from tests.initializers.wildberries_initializer import WildberriesTestDBFillerInitializer
from tests.providers.wildberries_test_provider import WildberriesUserMarketDataProviderImplTest


class WildberriesDBFillerWithKeyTest(BasicDBTest):
    @classmethod
    def get_db_init_flags_for_tests(cls) -> dict[str, list[TestDBContextAdditions]]:
        return {
            'test_fill_warehouses': [TestDBContextAdditions.MARKETPLACE]
        }

    def test_fill_warehouses(self):
        object_provider: WildberriesUserMarketDataProvider = WildberriesUserMarketDataProviderImplTest()
        with self.db_context.session() as session, session.begin():
            wildberries_object_filler: WildberriesDBFillerWithKey = \
                WildberriesDBFillerWithKeyImpl(session, object_provider, WildberriesTestDBFillerInitializer)
            wildberries_object_filler.fill_warehouse()
        with self.db_context.session() as session:
            warehouse_service = WarehouseService(WarehouseRepository(session), WarehouseTableToJormMapper())
            db_warehouse = warehouse_service.find_all_warehouses()
            self.assertEqual(10, len(db_warehouse))
