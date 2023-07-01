from jarvis_db.repositores.mappers.market.items import ProductTableToJormMapper
from jarvis_db.repositores.market.items import ProductCardRepository
from jarvis_db.services.market.items.product_card_service import ProductCardService

from jdu.db_tools import WildberriesDBFillerWithoutKeyImpl, \
    WildberriesDBFillerWithoutKey
from jdu.providers import WildBerriesDataProviderWithoutKey
from tests.basic_db_test import BasicDBTest, TestDBContextAdditions
from tests.provider_for_test.test_provider import WildBerriesDataProviderWithoutKeyImplTest


class ProductFillerTest(BasicDBTest):
    def get_additions_flags(self) -> list[TestDBContextAdditions]:
        return [TestDBContextAdditions.NICHE]

    def test_add_products(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImplTest()
        with self.db_context.session() as session, session.begin():
            object_filler: WildberriesDBFillerWithoutKey = WildberriesDBFillerWithoutKeyImpl(object_provider, session)
            object_filler.fill_products(10)
        with self.db_context.session() as session:
            service_product = ProductCardService(ProductCardRepository(session), ProductTableToJormMapper())
            db_products = service_product.find_all_in_niche(1)
            self.assertEqual(10, len(db_products))
