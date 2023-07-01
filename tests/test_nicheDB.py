from jarvis_db.repositores.mappers.market.infrastructure import NicheTableToJormMapper
from jarvis_db.repositores.market.infrastructure import NicheRepository
from jarvis_db.services.market.infrastructure.niche_service import NicheService

from jdu.db_tools import WildberriesDBFillerWithoutKeyImpl, \
    WildberriesDBFillerWithoutKey
from jdu.providers import WildBerriesDataProviderWithoutKey
from provider_for_test.test_provider import WildBerriesDataProviderWithoutKeyImplTest
from tests.basic_db_test import BasicDBTest, TestDBContextAdditions


class NicheFillerTest(BasicDBTest):
    def get_additions_flags(self) -> list[TestDBContextAdditions]:
        return [TestDBContextAdditions.CATEGORY]

    def test_fill_niches(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImplTest()
        with self.db_context.session() as session, session.begin():
            object_filler: WildberriesDBFillerWithoutKey = WildberriesDBFillerWithoutKeyImpl(object_provider, session)
            object_filler.fill_niches(10)
        with self.db_context.session() as session, session.begin():
            service_niche = NicheService(NicheRepository(session), NicheTableToJormMapper())
            db_niche = service_niche.find_all_in_marketplace(1)
            self.assertEqual(10, len(db_niche))
