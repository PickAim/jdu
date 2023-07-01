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
        product_num = 10
        products_global_ids: dict[int, tuple[str, int]] = \
            object_provider.get_products_id_to_name_cost_dict('Кофе зерновой', product_num)
        id_to_name_cost_list: list[tuple[int, str, int]] = [
            (global_id, products_global_ids[global_id][0], products_global_ids[global_id][1])
            for global_id in products_global_ids
        ]
        products: list[Product] = object_provider.get_products("Кофе зерновой", 'xuita', id_to_name_cost_list)
        print(f"products receiving time: {datetime.now() - before}")
        self.assertEqual(product_num, len(products))

    def test_get_niches(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImpl()
        before = datetime.now()
        niches_num = 10
        niche_names: list[str] = object_provider.get_niches_names("Автомобильные товары", niches_num)
        niches: list[Niche] = object_provider.get_niches(niche_names)
        print(f"niches receiving time: {datetime.now() - before}")
        self.assertEqual(niches_num, len(niches))

    def test_get_categories(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImpl()
        before = datetime.now()
        categories_num = 10
        category_names: list[str] = object_provider.get_categories_names(categories_num)
        categories: list[Category] = object_provider.get_categories(category_names)
        print(f"categories names receiving time: {datetime.now() - before}")
        self.assertEqual(categories_num, len(categories))

    def test_sorting(self):
        word = "Кофе"
        object_provider: WildBerriesDataProviderStandardImpl = \
            WildBerriesDataProviderStandardImpl('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
                                                '.eyJhY2Nlc3NJRCI6IjhiMGZkZWEwLWYxYjgtNDVjOS05NmM5LTdiMmRlNjU2N2Q3ZCJ9'
                                                '.6YAvO_GYeXW3em8WZ5cLynTBKcg8x5pmMmoCkgMY6QI')
        result = object_provider.get_nearest_keywords(word)
        self.assertEqual("готовый кофе", result[0])

    def test_get_warehouse(self):
        object_provider: WildBerriesDataProviderStandardImpl = \
            WildBerriesDataProviderStandardImpl(
                'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
                'eyJhY2Nlc3NJRCI6IjhiMGZkZWEwLWYxYjgtNDVjOS05NmM5LTdiMmRlNjU2N2Q3ZCJ9.'
                '6YAvO_GYeXW3em8WZ5cLynTBKcg8x5pmMmoCkgMY6QI')
        warehouses = object_provider.get_warehouses()
        self.assertNotEqual(len(warehouses), 0)

    def test_load_storage(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImpl()
        storage_data = object_provider.get_storage_dict(18681408)
        self.assertIsNotNone(storage_data)


if __name__ == '__main__':
    unittest.main()
