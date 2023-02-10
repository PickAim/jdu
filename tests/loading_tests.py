import unittest
from datetime import datetime

from jorm.market.items import Product

from jdu.providers.common import WildBerriesDataProviderWithoutKey
from jdu.providers.wildberries import WildBerriesDataProviderWithoutKeyImpl, WildBerriesDataProviderStandard


class LoadingTest(unittest.TestCase):

    def test_get_products_by_niche(self):
        # object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImpl()
        # self.assertNotEqual(0, len(object_provider.get_products_by_niche("Аварийное оборудование")))
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImpl()
        summary = 0
        n = 50
        for _ in range(n):
            before = datetime.now()
            products: list[Product] = object_provider.get_products_by_niche("Аварийное оборудование")
            summary += (datetime.now() - before).seconds
            print(f"receiving time: {datetime.now() - before}")
        print(f"middle_time: {summary / n}")

    def test_get_niche_by_category(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImpl()
        self.assertNotEqual(0, len(object_provider.get_niches_by_category("Аксессуары для малышей", 1, 1)))

    def test_get_categories(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImpl()
        self.assertNotEqual(0, len(object_provider.get_categories(1, 1, 1)))

    def test_sorting(self):
        word = "Кофе"
        object_provider: WildBerriesDataProviderStandard = \
            WildBerriesDataProviderStandard('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
                                            '.eyJhY2Nlc3NJRCI6IjhiMGZkZWEwLWYxYjgtNDVjOS05NmM5LTdiMmRlNjU2N2Q3ZCJ9'
                                            '.6YAvO_GYeXW3em8WZ5cLynTBKcg8x5pmMmoCkgMY6QI')
        result = object_provider.get_nearest_keywords(word)
        self.assertEqual("готовый кофе", result[0])

    def test_load_storage(self):
        product_id = 26414401
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImpl()
        storage_data: dict[int, dict[int, int]] = object_provider.get_storage_dict(product_id)
        self.assertIsNotNone(storage_data)
        self.assertEqual(2, len(storage_data.keys()))


if __name__ == '__main__':
    unittest.main()
