import unittest
import warnings
from datetime import datetime

from jorm.market.infrastructure import Niche, Category
from jorm.market.items import Product

from jdu.providers import WildBerriesDataProviderWithoutKey, \
    WildBerriesDataProviderWithoutKeyImpl, \
    WildBerriesDataProviderStandardImpl

warnings.filterwarnings(action="ignore", message="ResourceWarning: unclosed")


class LoadingTest(unittest.TestCase):

    def test_get_products_by_niche(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImpl()
        before = datetime.now()
        products_global_ids: dict[int, tuple[str, int]] = object_provider.get_products_id_to_name_cost_dict(
            'Кофе зерновой', 1, 100)
        products: list[Product] = object_provider.get_products("Кофе зерновой", products_global_ids,
                                                               list(products_global_ids.keys()))
        print(f"receiving time: {datetime.now() - before}")
        self.assertNotEqual(0, len(products))

    def test_get_niches(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImpl()
        before = datetime.now()
        niche_names: list[str] = object_provider.get_niches_names("Автомобильные товары", 10)
        niches: list[Niche] = object_provider.get_niches(niche_names)
        print(f"receiving time: {datetime.now() - before}")
        self.assertNotEqual(0, len(niches))

    def test_get_categories(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImpl()
        before = datetime.now()
        category_names: list[str] = object_provider.get_categories_names(10)
        categories: list[Category] = object_provider.get_categories(category_names)
        print(category_names)
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
        object_provider: WildBerriesDataProviderStandardImpl = \
            WildBerriesDataProviderStandardImpl('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
                                                '.eyJhY2Nlc3NJRCI6IjhiMGZkZWEwLWYxYjgtNDVjOS05NmM5LTdiMmRlNjU2N2Q3ZCJ9'
                                                '.6YAvO_GYeXW3em8WZ5cLynTBKcg8x5pmMmoCkgMY6QI')
        result = object_provider.get_nearest_keywords(word)
        self.assertEqual("готовый кофе", result[0])

    def test_load_storage(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImpl()
        for id in [18681408] * 100:
            storage_data = object_provider.get_storage_dict(id)
            storage_data = None
        # self.assertIsNotNone(storage_data)


if __name__ == '__main__':
    unittest.main()
