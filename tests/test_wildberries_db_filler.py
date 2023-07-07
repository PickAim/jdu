from jarvis_db.repositores.mappers.market.infrastructure import CategoryTableToJormMapper, NicheTableToJormMapper, \
    MarketplaceTableToJormMapper, WarehouseTableToJormMapper
from jarvis_db.repositores.mappers.market.items import ProductTableToJormMapper
from jarvis_db.repositores.market.infrastructure import CategoryRepository, NicheRepository, MarketplaceRepository
from jarvis_db.repositores.market.items import ProductCardRepository
from jarvis_db.services.market.infrastructure.category_service import CategoryService
from jarvis_db.services.market.infrastructure.marketplace_service import MarketplaceService
from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.services.market.items.product_card_service import ProductCardService

from jdu.db_tools.fill.db_fillers import StandardDBFiller
from jdu.db_tools.fill.wildberries_fillers import WildberriesDBFillerImpl
from jdu.providers.wildberries_providers import WildberriesDataProviderWithoutKey
from tests.basic_db_test import BasicDBTest, TestDBContextAdditions
from tests.providers.wildberries_test_provider import WildBerriesDataProviderWithoutKeyImplTest


class WildberriesDBFillerImplTest(BasicDBTest):
    @classmethod
    def get_db_init_flags_for_tests(cls) -> dict[str, list[TestDBContextAdditions]]:
        return {
            'test_fill_niches': [TestDBContextAdditions.CATEGORY],
            'test_fill_products': [TestDBContextAdditions.NICHE]
        }

    def test_init_marketplace(self):
        object_provider: WildberriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImplTest()
        with self.db_context.session() as session, session.begin():
            WildberriesDBFillerImpl(object_provider, session)
        with self.db_context.session() as session:
            marketplace_repository: MarketplaceRepository = MarketplaceRepository(session)
            service_marketplace = MarketplaceService(marketplace_repository,
                                                     MarketplaceTableToJormMapper(WarehouseTableToJormMapper()))
            marketplace, marketplace_id = service_marketplace.find_by_name('wildberries')
            self.assertEqual('wildberries', marketplace.name)

    def test_fill_categories(self):
        object_provider: WildberriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImplTest()
        with self.db_context.session() as session, session.begin():
            wildberries_object_filler: StandardDBFiller = \
                WildberriesDBFillerImpl(object_provider, session)
            wildberries_object_filler.fill_categories(10)
        with self.db_context.session() as session:
            service_category = CategoryService(CategoryRepository(session),
                                               CategoryTableToJormMapper(NicheTableToJormMapper()))

            db_category = service_category.find_all_in_marketplace(self.marketplace_id)
            self.assertEqual(10, len(db_category))

    def test_fill_niches(self):
        object_provider: WildberriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImplTest()
        with self.db_context.session() as session, session.begin():
            object_filler: StandardDBFiller = WildberriesDBFillerImpl(object_provider, session)
            object_filler.fill_niches(10)
        with self.db_context.session() as session, session.begin():
            service_niche = NicheService(NicheRepository(session), NicheTableToJormMapper())
            db_niche = service_niche.find_all_in_marketplace(1)
            self.assertEqual(10, len(db_niche))

    def test_fill_products(self):
        object_provider: WildberriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImplTest()
        with self.db_context.session() as session, session.begin():
            object_filler: StandardDBFiller = WildberriesDBFillerImpl(object_provider, session)
            object_filler.fill_products(10)
        with self.db_context.session() as session:
            service_product = ProductCardService(ProductCardRepository(session), ProductTableToJormMapper())
            db_products = service_product.find_all_in_niche(1)
            self.assertEqual(10, len(db_products))
