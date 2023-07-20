from datetime import datetime

from jarvis_db.factories.services import create_economy_service
from jorm.market.service import RequestInfo, FrequencyRequest, FrequencyResult

from jdu.db_tools.update.jorm_changer_impl import JormChangerImpl
from tests.basic_db_test import BasicDBTest, TestDBContextAdditions
from tests.test_utils import create_frequency_service, create_wb_db_filler


class FrequencyRequestTest(BasicDBTest):
    request_info = RequestInfo(date=datetime(2020, 2, 2), name="name")
    request = FrequencyRequest(BasicDBTest.test_niche_name, BasicDBTest.test_category_name, BasicDBTest.marketplace_id)
    result = FrequencyResult(x=[i for i in range(10)], y=[i for i in range(10)])

    @classmethod
    def get_db_init_flags_for_tests(cls) -> dict[str, list[TestDBContextAdditions]]:
        return {
            'test_change_frequency': [TestDBContextAdditions.NICHE, TestDBContextAdditions.USER],
            'test_remove_frequency': [TestDBContextAdditions.NICHE, TestDBContextAdditions.USER]
        }

    def test_change_frequency(self):
        with self.db_context.session() as session, session.begin():
            wildberries_changer = JormChangerImpl(create_economy_service(session),
                                                  create_frequency_service(session),
                                                  create_wb_db_filler(session))
            wildberries_changer.save_frequency_request(self.request,
                                                       self.result,
                                                       self.request_info,
                                                       self.user_id
                                                       )
        with self.db_context.session() as session:
            service = create_frequency_service(session)
            db_economy = service.find_user_requests(self.user_id)
            self.assertEqual(len(db_economy), 1)

    def test_remove_frequency(self):
        with self.db_context.session() as session, session.begin():
            wildberries_changer = JormChangerImpl(create_economy_service(session),
                                                  create_frequency_service(session),
                                                  create_wb_db_filler(session))
            request_id = wildberries_changer.save_frequency_request(self.request,
                                                                    self.result,
                                                                    self.request_info,
                                                                    self.user_id
                                                                    )
            wildberries_changer.delete_frequency_request(request_id, self.user_id)
        with self.db_context.session() as session:
            service = create_frequency_service(session)
            db_frequency_requests = service.find_user_requests(self.user_id)
            self.assertEqual(0, len(db_frequency_requests))
