import unittest

from jarvis_db.repositores.mappers.market.infrastructure import CategoryTableToJormMapper, NicheTableToJormMapper
from jarvis_db.repositores.market.infrastructure import CategoryRepository
from jarvis_db.services.market.infrastructure.category_service import CategoryService
from jarvis_db.tables import Marketplace

from jdu.db_access.fill.db_fillers import WildberriesDbFiller, WildberriesDBFillerImpl
from jdu.providers.common import WildBerriesDataProviderWithoutKey
from tests.db_context import DbContext
from tests.provider_for_test.test_provider import WildBerriesDataProviderWithoutKeyImplTest


class CategoryTest(unittest.TestCase):

    def setUp(self):
        self.__db_context = DbContext()
        with self.__db_context.session() as session, session.begin():
            marketplace = Marketplace(name='wildberries')
            session.add(marketplace)
            session.flush()
            self.__marketplace_id = marketplace.id

    def test_fill_categories(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImplTest()
        with self.__db_context.session() as session, session.begin():
            object_filler: WildberriesDbFiller = WildberriesDBFillerImpl(object_provider, session)
            object_filler.fill_categories(10)
        with self.__db_context.session() as session:
            service_category = CategoryService(CategoryRepository(session),
                                               CategoryTableToJormMapper(NicheTableToJormMapper()))

            db_category = service_category.find_all_in_marketplace(1)
            self.assertEqual(len(db_category), 10)
