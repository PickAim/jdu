import unittest
import warnings
from datetime import datetime

from jorm.market.infrastructure import Niche, Category
from jorm.market.items import Product

from jdu.providers.common import WildBerriesDataProviderWithoutKey
from jdu.providers.wildberries import WildBerriesDataProviderWithoutKeyImpl, WildBerriesDataProviderStandard

warnings.filterwarnings(action="ignore", message="ResourceWarning: unclosed")


class LoadingTest(unittest.TestCase):

    def test_get_products_by_niche(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImpl()
        before = datetime.now()
        products: list[Product] = object_provider.get_products_by_niche("Кофе зерновой", 1)
        print(f"receiving time: {datetime.now() - before}")
        self.assertNotEqual(0, len(products))

    def test_get_niche_by_category(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImpl()
        before = datetime.now()
        niches: list[Niche] = object_provider.get_niches_by_category("Аксессуары для малышей", 1, 1)
        print(f"receiving time: {datetime.now() - before}")
        self.assertNotEqual(0, len(niches))

    def test_get_categories(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImpl()
        before = datetime.now()
        categories: list[Category] = object_provider.get_categories(1, 1, 1)
        print(f"receiving time: {datetime.now() - before}")
        print(f'category size: {len(categories)}\n')
        summary = 0
        for category in categories:
            summary += len(category.niches)
        print(f'niches number: {summary}\n')
        summary = 0
        for category in categories:
            for niche_key in category.niches:
                summary += len(category.niches[niche_key].products)
        print(f'product number: {summary}\n')
        self.assertNotEqual(0, len(categories))

    def test_sorting(self):
        word = "Кофе"
        object_provider: WildBerriesDataProviderStandard = \
            WildBerriesDataProviderStandard('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
                                            '.eyJhY2Nlc3NJRCI6IjhiMGZkZWEwLWYxYjgtNDVjOS05NmM5LTdiMmRlNjU2N2Q3ZCJ9'
                                            '.6YAvO_GYeXW3em8WZ5cLynTBKcg8x5pmMmoCkgMY6QI')
        result = object_provider.get_nearest_keywords(word)
        self.assertEqual("готовый кофе", result[0])

    def _test_load_storage(self):
        product_ids = [26414401, 6170053]
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImpl()
        storage_data: dict[int, dict[int, int]] = object_provider.get_storage_data(product_ids)
        self.assertIsNotNone(storage_data)
        self.assertEqual(2, len(storage_data.keys()))


if __name__ == '__main__':
    unittest.main()
