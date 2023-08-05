import unittest

from jarvis_db.factories.services import create_warehouse_service

from tests.basic_db_test import TestDBContextAdditions, BasicDBTest
from tests.test_utils import create_jorm_changer


class JORMChangerTest(BasicDBTest):
    @classmethod
    def get_db_init_flags_for_tests(cls) -> dict[str, list[TestDBContextAdditions]]:
        return {
            'test_fill_warehouses': [TestDBContextAdditions.USER_API_KEY]
        }

    def test_fill_warehouses(self):
        with self.db_context.session() as session, session.begin():
            jorm_changer = create_jorm_changer(session)
            loaded_warehouses = jorm_changer.load_user_warehouse(self.user_id, self.marketplace_id)
            self.assertIsNotNone(loaded_warehouses)
        with self.db_context.session() as session:
            warehouse_service = create_warehouse_service(session)
            db_warehouse = warehouse_service.find_all_warehouses(self.marketplace_id)
            self.assertEqual(11, len(db_warehouse))  # +1 for default marketplace warehouse


if __name__ == '__main__':
    unittest.main()
