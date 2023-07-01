from jarvis_db.repositores.mappers.market.items import ProductHistoryTableToJormMapper
from jarvis_db.repositores.mappers.market.items.leftover_mappers import LeftoverTableToJormMapper
from jarvis_db.repositores.market.infrastructure import WarehouseRepository
from jarvis_db.repositores.market.items import ProductHistoryRepository
from jarvis_db.repositores.market.items.leftover_repository import LeftoverRepository
from jarvis_db.services.market.items.leftover_service import LeftoverService
from jarvis_db.services.market.items.product_history_service import ProductHistoryService
from jarvis_db.services.market.items.product_history_unit_service import ProductHistoryUnitService

from jdu.db_tools import WildberriesDBFillerWithoutKeyImpl, \
    WildberriesDBFillerWithoutKey
from jdu.providers import WildBerriesDataProviderWithoutKey
from provider_for_test.test_provider import WildBerriesDataProviderWithoutKeyImplTest
from tests.basic_db_test import BasicDBTest, TestDBContextAdditions


class PriceHistoryFillerTest(BasicDBTest):
    def get_additions_flags(self) -> list[TestDBContextAdditions]:
        return [TestDBContextAdditions.PRODUCT]

    def test_fill_price_history(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImplTest()
        with self.db_context.session() as session, session.begin():
            wildberries_object_filler: WildberriesDBFillerWithoutKey = WildberriesDBFillerWithoutKeyImpl(
                object_provider, session)
            wildberries_object_filler.fill_price_history(self.test_niche_name)
        with self.db_context.session() as session:
            history_unit_service = ProductHistoryUnitService(ProductHistoryRepository(session))
            price_history_service = ProductHistoryService(history_unit_service, LeftoverService(
                LeftoverRepository(session), WarehouseRepository(session), history_unit_service),
                                                          ProductHistoryRepository(session),
                                                          ProductHistoryTableToJormMapper(
                                                              LeftoverTableToJormMapper()))
            db_price_history = price_history_service.find_product_history(self.product_id)
            self.assertEqual(10, len(db_price_history.get_history()))
