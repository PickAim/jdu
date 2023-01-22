import unittest
import time
from os.path import join

import numpy as np

from jdu.request.loader_utils import get_nearest_keywords, load_niche_info, get_storage_data, load_cost_data_from_file
from jdu.request.request_utils import get_parents, get_object_names
from jdu.services import constants


class LoadingTest(unittest.TestCase):
    def test_sorting(self):
        word = "Кофе"
        result = get_nearest_keywords(word)
        self.assertEqual("готовый кофе", result[0])

    def test_load(self):
        text_to_search = 'Кофе'
        is_update = True
        pages_num = 1
        start_time = time.time()
        load_niche_info(text_to_search, constants.data_path, is_update, pages_num)
        print(time.time() - start_time)
        filename = str(join(constants.data_path, text_to_search + ".txt"))
        costs = np.array(load_cost_data_from_file(filename))
        self.assertNotEqual(0, len(costs))

    def test_load_storage(self):
        product_ids = [26414401, 6170053]
        storage_data: dict[int, dict[int, int]] = get_storage_data(product_ids)
        self.assertIsNotNone(storage_data)
        self.assertEqual(2, len(storage_data.keys()))

    def test_get_parents(self):
        parent_categories = get_parents()
        self.assertNotEqual(len(parent_categories), 0)

    def test_get_objects_name(self):
        text_object = "Кофе"
        object_names = get_object_names(text_object)
        self.assertNotEqual(len(object_names), 0)


if __name__ == '__main__':
    unittest.main()
