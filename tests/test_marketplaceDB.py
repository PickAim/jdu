import unittest

from jarvis_db.repositores.mappers.market.infrastructure.marketplace_mappers import \
    MarketplaceTableToJormMapper
from jarvis_db.repositores.mappers.market.infrastructure.warehouse_mappers import \
    WarehouseTableToJormMapper
from jarvis_db.repositores.market.infrastructure.marketplace_repository import \
    MarketplaceRepository
from jarvis_db.services.market.infrastructure.marketplace_service import \
    MarketplaceService

from jdu.db_tools import WildberriesDBFillerImpl
from jdu.providers import WildBerriesDataProviderWithoutKey
from tests.db_context import DbContext
from tests.provider_for_test import WildBerriesDataProviderWithoutKeyImplTest


class MarketplaceFillerTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext()

    def test_fill_marketplace(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImplTest()
        with self.__db_context.session() as session, session.begin():
            WildberriesDBFillerImpl(object_provider, session)
        with self.__db_context.session() as session:
            marketplace_repository: MarketplaceRepository = MarketplaceRepository(
                session)
            service_marketplace = MarketplaceService(marketplace_repository,
                                                     MarketplaceTableToJormMapper(WarehouseTableToJormMapper()))
            marketplace, marketplace_id = service_marketplace.find_by_name('wildberries')
            self.assertEqual('wildberries', marketplace.name)
