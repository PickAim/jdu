from datetime import datetime

from jorm.market.service import RequestInfo, FrequencyRequest, FrequencyResult

from jdu.db_tools.update.jorm_changer_impl import JormChangerImpl
from tests.basic_db_test import BasicDBTest, TestDBContextAdditions
from tests.test_utils import create_economy_service, create_frequency_service


class FrequencyRequestTest(BasicDBTest):
    request_info = RequestInfo(date=datetime(2020, 2, 2), name="name")
    request = FrequencyRequest(BasicDBTest.test_niche_name, BasicDBTest.test_category_name, BasicDBTest.marketplace_id)
    result = FrequencyResult({i: i + 1 for i in range(10)})

    @classmethod
    def get_db_init_flags_for_tests(cls) -> dict[str, list[TestDBContextAdditions]]:
        return {
            '_test_change_frequency': [TestDBContextAdditions.NICHE, TestDBContextAdditions.USER],
            '_test_remove_frequency': [TestDBContextAdditions.NICHE, TestDBContextAdditions.USER]
        }

    def _test_change_frequency(self):  # TODO waiting for JDB mapping fixes
        with self.db_context.session() as session, session.begin():
            wildberries_changer = JormChangerImpl(create_economy_service(session),
                                                  create_frequency_service(session))
            wildberries_changer.save_frequency_request(self.request,
                                                       self.result,
                                                       self.request_info,
                                                       self.user_id
                                                       )
        with self.db_context.session() as session:
            service = create_frequency_service(session)
            db_economy = service.find_user_requests(self.user_id)
            self.assertEqual(len(db_economy), 1)

    def _test_remove_frequency(self):  # TODO waiting for JDB mapping fixes
        request_id = 1
        with self.db_context.session() as session, session.begin():
            wildberries_changer = JormChangerImpl(create_economy_service(session),
                                                  create_frequency_service(session))
            wildberries_changer.save_frequency_request(self.request,
                                                       self.result,
                                                       self.request_info,
                                                       self.user_id
                                                       )
            wildberries_changer.delete_frequency_request(request_id, self.user_id)
        with self.db_context.session() as session:
            service = create_frequency_service(session)
            db_economy = service.find_user_requests(self.user_id)
            self.assertEqual(len(db_economy), 0)
