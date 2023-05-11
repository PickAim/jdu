import unittest

from jarvis_db.repositores.mappers.market.items import ProductTableToJormMapper
from jarvis_db.repositores.market.items import ProductCardRepository
from jarvis_db.services.market.items.product_card_service import ProductCardService
from jarvis_db.tables import Marketplace, Category, Niche

from db_context import DbContext
from jdu.db_tools import WildberriesDBFillerImpl, \
    WildberriesDBFiller
from jdu.providers import WildBerriesDataProviderWithoutKey
from tests.provider_for_test.test_provider import WildBerriesDataProviderWithoutKeyImplTest


class ProductFillerTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext()
        with self.__db_context.session() as session, session.begin():
            marketplace = Marketplace(name='wildberries')
            category = Category(name='Автомобильные товары', marketplace=marketplace)
            niche = Niche(
                name='Аварийное оборудование',
                marketplace_commission=1,
                partial_client_commission=1,
                client_commission=1,
                return_percent=1,
                category=category)
            session.add(niche)
            session.flush()
            self.__niche_id = niche.id

    @unittest.expectedFailure  # TODO rework JDB
    def test_add_products(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImplTest()
        with self.__db_context.session() as session, session.begin():
            object_filler: WildberriesDBFiller = WildberriesDBFillerImpl(object_provider, session)
            object_filler.fill_products(1, 10)
        with self.__db_context.session() as session:
            service_product = ProductCardService(ProductCardRepository(session), ProductTableToJormMapper())
            db_products = service_product.find_all_in_niche(1)
            self.assertEqual(len(db_products), 10)
