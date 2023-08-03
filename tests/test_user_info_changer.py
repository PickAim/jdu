import unittest

from jarvis_db.factories.services import create_user_service
from jorm.jarvis.db_update import UserInfoChanger
from jorm.market.person import User

from tests.basic_db_test import BasicDBTest, TestDBContextAdditions
from tests.test_utils import create_user_info_changer


class UserInfoChangerTest(BasicDBTest):
    # TODO let's create test for ideally every method of UserInfoChanger

    @classmethod
    def get_db_init_flags_for_tests(cls) -> dict[str, list[TestDBContextAdditions]]:
        return {
            "test_api_key_adding": [TestDBContextAdditions.MARKETPLACE, TestDBContextAdditions.USER]
        }

    def test_api_key_adding(self):
        # TODO think about extending this test to test api key removing in next JORM version
        test_api_key = "test_api_key"
        with self.db_context.session() as session, session.begin():
            user_info_changer: UserInfoChanger = create_user_info_changer(session)
            user_info_changer.add_marketplace_api_key(test_api_key, self.user_id, self.marketplace_id)
        with self.db_context.session() as session, session.begin():
            user_service = create_user_service(session)
            user: User = user_service.find_by_id(self.user_id)
            self.assertEqual(1, len(user.marketplace_keys))
            self.assertEqual(test_api_key, user.marketplace_keys[self.marketplace_id])


if __name__ == '__main__':
    unittest.main()
