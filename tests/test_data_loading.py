import unittest
import warnings
from datetime import datetime

from jorm.market.infrastructure import Niche, Category
from jorm.market.items import Product

from jdu.providers.wildberries_providers import WildberriesDataProviderWithoutKey, WildberriesUserMarketDataProvider, \
    WildberriesUserMarketDataProviderImpl, WildberriesDataProviderWithoutKeyImpl
from jdu.support.types import ProductInfo
from tests.basic_db_test import AUTH_KEY

warnings.filterwarnings(action="ignore", message="ResourceWarning: unclosed")


class LoadingTest(unittest.TestCase):
    def test_get_products_by_niche(self):
        object_provider: WildberriesDataProviderWithoutKey = WildberriesDataProviderWithoutKeyImpl()
        before = datetime.now()
        product_num = 10
        products_info: set[ProductInfo] = \
            object_provider.get_products_mapped_info('Кофе зерновой', product_num)
        products: list[Product] = object_provider.get_products("Кофе зерновой", 'xuita', list(products_info))
        print(f"products receiving time: {datetime.now() - before}")
        self.assertEqual(product_num, len(products))

    def test_get_niches(self):
        object_provider: WildberriesDataProviderWithoutKey = WildberriesDataProviderWithoutKeyImpl()
        before = datetime.now()
        niches_num = 10
        niche_names: list[str] = object_provider.get_niches_names("Автомобильные товары", niches_num)
        niches: list[Niche] = object_provider.get_niches(niche_names)
        print(f"niches receiving time: {datetime.now() - before}")
        self.assertEqual(niches_num, len(niches))

    def test_get_categories(self):
        object_provider: WildberriesDataProviderWithoutKey = WildberriesDataProviderWithoutKeyImpl()
        before = datetime.now()
        categories_num = 10
        category_names: list[str] = object_provider.get_categories_names(categories_num)
        categories: list[Category] = object_provider.get_categories(category_names)
        print(f"categories names receiving time: {datetime.now() - before}")
        self.assertEqual(categories_num, len(categories))

    def test_sorting(self):
        word = "Кофе"
        object_provider: WildberriesUserMarketDataProvider = \
            WildberriesUserMarketDataProviderImpl(AUTH_KEY)
        result = object_provider.get_nearest_keywords(word)
        self.assertEqual("готовый кофе", result[0])

    def test_get_warehouse(self):
        object_provider: WildberriesUserMarketDataProvider = \
            WildberriesUserMarketDataProviderImpl(AUTH_KEY)
        warehouses = object_provider.get_warehouses()
        self.assertNotEqual(len(warehouses), 0)

    def test_load_storage(self):
        object_provider: WildberriesDataProviderWithoutKey = WildberriesDataProviderWithoutKeyImpl()
        storage_data = object_provider.get_storage_dict(18681408)
        self.assertIsNotNone(storage_data)


if __name__ == '__main__':
    unittest.main()
