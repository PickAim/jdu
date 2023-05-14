import unittest
import warnings

from jarvis_db.repositores.mappers.market.infrastructure import NicheTableToJormMapper
from jarvis_db.repositores.market.infrastructure import NicheRepository
from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.tables import Marketplace, Category

from jdu.db_tools import WildberriesDBFillerImpl, \
    WildberriesDBFiller
from jdu.providers import WildBerriesDataProviderWithoutKey
from provider_for_test.test_provider import WildBerriesDataProviderWithoutKeyImplTest
from tests.db_context import DbContext

warnings.filterwarnings(action="ignore", message="ResourceWarning: unclosed")


class NicheFillerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.__db_context = DbContext()
        with self.__db_context.session() as session, session.begin():
            marketplace = Marketplace(name='wildberries')
            category = Category(name='Category_1', marketplace=marketplace)
            session.add(category)
            session.flush()
            self.__category_id = category.id
            self.__marketplace_id = marketplace.id

    def test_fill_niches(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImplTest()
        with self.__db_context.session() as session, session.begin():
            object_filler: WildberriesDBFiller = WildberriesDBFillerImpl(object_provider, session)
            object_filler.fill_niches(10)
        with self.__db_context.session() as session, session.begin():
            service_niche = NicheService(NicheRepository(session), NicheTableToJormMapper())
            db_niche = service_niche.find_all_in_marketplace(1)
            self.assertEqual(len(db_niche), 10)
