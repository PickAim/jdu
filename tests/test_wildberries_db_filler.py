from jarvis_db.factories.services import create_marketplace_service, create_category_service, create_niche_service, \
    create_product_card_service
from jorm.support.constants import DEFAULT_CATEGORY_NAME

from jdu.db_tools.fill.db_fillers import StandardDBFiller
from jdu.support.constant import WILDBERRIES_NAME
from tests.basic_db_test import BasicDBTest, TestDBContextAdditions
from tests.test_utils import create_wb_db_filler, create_wb_data_provider_without_key, \
    create_wb_real_data_provider_without_key


class WildberriesDBFillerImplTest(BasicDBTest):
    @classmethod
    def get_db_init_flags_for_tests(cls) -> dict[str, list[TestDBContextAdditions]]:
        return {
            'test_fill_niches': [TestDBContextAdditions.CATEGORY],
            'test_fill_products': [TestDBContextAdditions.NICHE],
            'test_fill_loaded_products': [TestDBContextAdditions.CATEGORY, TestDBContextAdditions.WAREHOUSES]
        }

    def test_init_marketplace(self):
        with self.db_context.session() as session, session.begin():
            create_wb_db_filler(session)
        with self.db_context.session() as session:
            service_marketplace = create_marketplace_service(session)
            marketplace, marketplace_id = service_marketplace.find_by_name(WILDBERRIES_NAME)
            self.assertEqual(WILDBERRIES_NAME, marketplace.name)

    def test_fill_categories(self):
        with self.db_context.session() as session, session.begin():
            wildberries_db_filler: StandardDBFiller = create_wb_db_filler(session)
            provider = create_wb_data_provider_without_key()
            category_service = create_category_service(session)
            wildberries_db_filler.fill_categories(category_service, provider, 10)
        with self.db_context.session() as session:
            category_service = create_category_service(session)
            db_category = category_service.find_all_in_marketplace(self.marketplace_id)
            self.assertEqual(10, len(db_category))

    def test_fill_niches(self):
        with self.db_context.session() as session, session.begin():
            db_filler: StandardDBFiller = create_wb_db_filler(session)
            provider = create_wb_data_provider_without_key()
            category_service = create_category_service(session)
            niche_service = create_niche_service(session)
            db_filler.fill_niches(category_service, niche_service, provider, 10)
        with self.db_context.session() as session, session.begin():
            service_niche = create_niche_service(session)
            db_niche = service_niche.find_all_in_marketplace(1)
            self.assertEqual(10, len(db_niche))

    def test_fill_loaded_products(self):
        product_num = 10
        loaded_niche_name = 'Кофе'
        with self.db_context.session() as session, session.begin():
            db_filler: StandardDBFiller = create_wb_db_filler(session)
            provider = create_wb_data_provider_without_key()
            category_service = create_category_service(session)
            niche_service = create_niche_service(session)
            product_card_service = create_product_card_service(session)
            loaded_niche = db_filler.fill_niche_by_name(category_service, niche_service,
                                                        product_card_service, provider, loaded_niche_name, product_num)
            self.assertIsNotNone(loaded_niche)
        with self.db_context.session() as session:
            category_service = create_category_service(session)
            found_category_info = category_service.find_by_name(DEFAULT_CATEGORY_NAME, self.marketplace_id)
            self.assertIsNotNone(found_category_info)
            _, category_id = found_category_info
            niche_service = create_niche_service(session)
            found_niche_info = niche_service.find_by_name(loaded_niche_name, category_id)
            self.assertIsNotNone(found_niche_info)
            _, niche_id = found_niche_info
            product_service = create_product_card_service(session)
            db_products = product_service.find_all_in_niche(niche_id)
            self.assertEqual(len(loaded_niche.products), len(db_products))

    def test_non_fill_loaded_niche(self):
        product_num = 10
        loaded_niche_name = 'странная aglh ниша adglhagdasf'
        with self.db_context.session() as session, session.begin():
            db_filler: StandardDBFiller = create_wb_db_filler(session)
            provider = create_wb_real_data_provider_without_key()
            category_service = create_category_service(session)
            niche_service = create_niche_service(session)
            product_card_service = create_product_card_service(session)
            loaded_niche = db_filler.fill_niche_by_name(category_service, niche_service,
                                                        product_card_service, provider, loaded_niche_name, product_num)
            print(loaded_niche)
            self.assertIsNone(loaded_niche)
        with self.db_context.session() as session:
            category_service = create_category_service(session)
            found_category_info = category_service.find_by_name(DEFAULT_CATEGORY_NAME, self.marketplace_id)
            self.assertIsNotNone(found_category_info)
            _, category_id = found_category_info
            niche_service = create_niche_service(session)
            found_niche_info = niche_service.find_by_name(loaded_niche_name, category_id)
            self.assertIsNone(found_niche_info)
