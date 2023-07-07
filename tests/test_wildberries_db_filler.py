from jarvis_db.repositores.mappers.market.infrastructure import CategoryTableToJormMapper, NicheTableToJormMapper, \
    MarketplaceTableToJormMapper, WarehouseTableToJormMapper
from jarvis_db.repositores.mappers.market.items import ProductTableToJormMapper
from jarvis_db.repositores.market.infrastructure import CategoryRepository, NicheRepository, MarketplaceRepository
from jarvis_db.repositores.market.items import ProductCardRepository
from jarvis_db.services.market.infrastructure.category_service import CategoryService
from jarvis_db.services.market.infrastructure.marketplace_service import MarketplaceService
from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.services.market.items.product_card_service import ProductCardService
from jorm.support.constants import DEFAULT_CATEGORY_NAME

from jdu.db_tools.fill.db_fillers import StandardDBFiller
from jdu.db_tools.fill.wildberries_fillers import WildberriesDBFillerImpl
from jdu.providers.wildberries_providers import WildberriesDataProviderWithoutKey, WildberriesDataProviderWithoutKeyImpl
from tests.basic_db_test import BasicDBTest, TestDBContextAdditions
from tests.providers.wildberries_test_provider import WildBerriesDataProviderWithoutKeyImplTest


class WildberriesDBFillerImplTest(BasicDBTest):
    @classmethod
    def get_db_init_flags_for_tests(cls) -> dict[str, list[TestDBContextAdditions]]:
        return {
            'test_fill_niches': [TestDBContextAdditions.CATEGORY],
            'test_fill_products': [TestDBContextAdditions.NICHE],
            'test_fill_loaded_products': [TestDBContextAdditions.CATEGORY]
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
            wildberries_db_filler: StandardDBFiller = \
                WildberriesDBFillerImpl(object_provider, session)
            wildberries_db_filler.fill_categories(10)
        with self.db_context.session() as session:
            category_service = CategoryService(CategoryRepository(session),
                                               CategoryTableToJormMapper(NicheTableToJormMapper()))

            db_category = category_service.find_all_in_marketplace(self.marketplace_id)
            self.assertEqual(10, len(db_category))

    def test_fill_niches(self):
        object_provider: WildberriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImplTest()
        with self.db_context.session() as session, session.begin():
            db_filler: StandardDBFiller = WildberriesDBFillerImpl(object_provider, session)
            db_filler.fill_niches(10)
        with self.db_context.session() as session, session.begin():
            service_niche = NicheService(NicheRepository(session), NicheTableToJormMapper())
            db_niche = service_niche.find_all_in_marketplace(1)
            self.assertEqual(10, len(db_niche))

    def test_fill_products(self):
        product_num = 10
        object_provider: WildberriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImplTest()
        with self.db_context.session() as session, session.begin():
            db_filler: StandardDBFiller = WildberriesDBFillerImpl(object_provider, session)
            db_filler.fill_products(product_num)
        with self.db_context.session() as session:
            product_service = ProductCardService(ProductCardRepository(session), ProductTableToJormMapper())
            db_products = product_service.find_all_in_niche(self.niche_id)
            self.assertEqual(product_num, len(db_products))

    def test_fill_loaded_products(self):
        product_num = 10
        loaded_niche_name = 'Кофе'
        object_provider: WildberriesDataProviderWithoutKey = WildberriesDataProviderWithoutKeyImpl()
        with self.db_context.session() as session, session.begin():
            db_filler: StandardDBFiller = WildberriesDBFillerImpl(object_provider, session)
            loaded_niche = db_filler.fill_niche_by_name(loaded_niche_name)
            self.assertIsNotNone(loaded_niche)
        with self.db_context.session() as session:
            category_service = CategoryService(CategoryRepository(session),
                                               CategoryTableToJormMapper(NicheTableToJormMapper()))
            found_category_info = category_service.find_by_name(DEFAULT_CATEGORY_NAME, self.marketplace_id)
            self.assertIsNotNone(found_category_info)
            _, category_id = found_category_info
            niche_service = NicheService(NicheRepository(session), NicheTableToJormMapper())
            found_niche_info = niche_service.find_by_name(loaded_niche_name, category_id)
            self.assertIsNotNone(found_niche_info)
            _, niche_id = found_niche_info
            product_service = ProductCardService(ProductCardRepository(session), ProductTableToJormMapper())
            db_products = product_service.find_all_in_niche(niche_id)
            self.assertEqual(len(loaded_niche.products), len(db_products))
