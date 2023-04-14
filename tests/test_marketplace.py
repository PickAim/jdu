import unittest

from jarvis_db.repositores.mappers.market.infrastructure.marketplace_mappers import \
    MarketplaceTableToJormMapper
from jarvis_db.repositores.mappers.market.infrastructure.warehouse_mappers import \
    WarehouseTableToJormMapper
from jarvis_db.repositores.market.infrastructure.marketplace_repository import \
    MarketplaceRepository
from jarvis_db.services.market.infrastructure.marketplace_service import \
    MarketplaceService

from jdu.db_access.fill.db_fillers import WildberriesDbFiller, WildberriesDBFillerImpl
from jdu.providers.common import WildBerriesDataProviderWithoutKey
from tests.db_context import DbContext
from tests.provider_for_test.test_provider import WildBerriesDataProviderWithoutKeyImplTest


class MarketplaceServiceTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext()

    def test_create(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImplTest()
        with self.__db_context.session() as session, session.begin():
            object_filler: WildberriesDbFiller = WildberriesDBFillerImpl(object_provider, session)
            object_filler.fill_marketplace()
        with self.__db_context.session() as session:
            marketplace_repository: MarketplaceRepository = MarketplaceRepository(
                session)
            service_marketplace = MarketplaceService(marketplace_repository,
                                                     MarketplaceTableToJormMapper(WarehouseTableToJormMapper()))
            marketplace, marketplace_id = service_marketplace.find_by_name('wildberries')
            self.assertEqual('wildberries', marketplace.name)
