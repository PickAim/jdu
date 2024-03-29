import unittest
import warnings
from datetime import datetime

from jorm.market.infrastructure import Niche, Category
from jorm.market.items import Product

from jdu.providers.wildberries_providers import WildberriesDataProviderWithoutKey, WildberriesUserMarketDataProvider
from test_utils import create_wb_data_provider_with_key, \
    create_wb_data_provider_without_key

warnings.filterwarnings(action="ignore", message="ResourceWarning: unclosed")


class LoadingTest(unittest.TestCase):
    def test_get_products_by_niche(self):
        object_provider: WildberriesDataProviderWithoutKey = create_wb_data_provider_without_key()
        before = datetime.now()
        product_num = 10
        products_ids = object_provider.get_products_globals_ids('Кофе зерновой', product_num)
        products: list[Product] = object_provider.get_products("Кофе зерновой", 'xuita', list(products_ids))
        print(f"products receiving time: {datetime.now() - before}")
        self.assertEqual(product_num, len(products))

    def test_get_niches(self):
        object_provider: WildberriesDataProviderWithoutKey = create_wb_data_provider_without_key()
        before = datetime.now()
        niches_num = 10
        niche_names: list[str] = object_provider.get_niches_names("Автомобильные товары", niches_num)
        niches: list[Niche] = object_provider.get_niches(niche_names)
        print(f"niches receiving time: {datetime.now() - before}")
        self.assertEqual(niches_num, len(niches))

    def test_get_categories(self):
        object_provider: WildberriesDataProviderWithoutKey = create_wb_data_provider_without_key()
        before = datetime.now()
        categories_num = 10
        category_names: list[str] = object_provider.get_categories_names(categories_num)
        categories: list[Category] = object_provider.get_categories(category_names)
        print(f"categories names receiving time: {datetime.now() - before}")
        self.assertEqual(categories_num, len(categories))

    def test_keywords_loading(self):
        word = "Кофе"
        object_provider: WildberriesUserMarketDataProvider = create_wb_data_provider_with_key()
        result = object_provider.get_nearest_keywords(word)
        self.assertNotEqual(0, len(result))

    def test_get_warehouse(self):
        object_provider: WildberriesDataProviderWithoutKey = create_wb_data_provider_without_key()
        warehouses = object_provider.get_warehouses_from_file()
        self.assertNotEqual(0, len(warehouses))

    def test_get_user_products(self):
        object_provider: WildberriesUserMarketDataProvider = create_wb_data_provider_with_key()
        products_ids = object_provider.get_user_products()
        self.assertNotEqual(len(products_ids), 0)

    def test_load_storage(self):
        object_provider: WildberriesDataProviderWithoutKey = create_wb_data_provider_without_key()
        storage_data = object_provider.get_storage_dict(18681408)
        self.assertIsNotNone(storage_data)

    # def test_load_top_request(self):
    #     object_provider: WildberriesDataProviderWithoutKey = create_wb_data_provider_without_key()
    #     storage_data = object_provider.get_top_request_by_marketplace_query('month', 1000)
    #     self.assertIsNotNone(storage_data)


if __name__ == '__main__':
    unittest.main()
