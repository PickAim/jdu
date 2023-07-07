from datetime import datetime

from jorm.market.service import RequestInfo, UnitEconomyRequest, UnitEconomyResult

from jdu.db_tools.update.jorm_changer_impl import JormChangerImpl
from tests.basic_db_test import BasicDBTest, TestDBContextAdditions
from tests.test_utils import create_economy_service, create_frequency_service, create_wb_db_filler


class AccountServiceTest(BasicDBTest):
    @classmethod
    def get_db_init_flags_for_tests(cls) -> dict[str, list[TestDBContextAdditions]]:
        return {
            'test_change_unit_economy': [TestDBContextAdditions.NICHE,
                                         TestDBContextAdditions.WAREHOUSE,
                                         TestDBContextAdditions.USER],
            'test_remove_unit_economy': [TestDBContextAdditions.NICHE,
                                         TestDBContextAdditions.WAREHOUSE,
                                         TestDBContextAdditions.USER]
        }

    def test_change_unit_economy(self):
        request_info = RequestInfo(date=datetime(2020, 10, 23), name="name")
        request_entity = UnitEconomyRequest(
            100,
            20,
            self.test_niche_name,
            self.test_category_name,
            self.marketplace_id,
            transit_count=11,
            transit_price=121,
            market_place_transit_price=33,
            warehouse_name=self.test_warehouse_name,
        )
        result = UnitEconomyResult(200, 300, 12, 25, 151, 134, 12355, 2, 1.2, 2.0)
        with self.db_context.session() as session, session.begin():
            wildberries_changer = JormChangerImpl(create_economy_service(session),
                                                  create_frequency_service(session),
                                                  create_wb_db_filler(session))
            wildberries_changer.save_unit_economy_request(request_entity,
                                                          result,
                                                          request_info,
                                                          self.user_id)
        with self.db_context.session() as session:
            service = create_economy_service(session)
            db_economy = service.find_user_requests(1)
            self.assertEqual(len(db_economy), 1)

    def test_remove_unit_economy(self):
        request_id = 1
        result_id = 1
        with self.db_context.session() as session, session.begin():
            wildberries_changer = JormChangerImpl(create_economy_service(session),
                                                  create_frequency_service(session),
                                                  create_wb_db_filler(session))
            wildberries_changer.delete_unit_economy_request(request_id, result_id)
        with self.db_context.session() as session:
            service = create_economy_service(session)
            db_economy = service.find_user_requests(1)
            self.assertEqual(len(db_economy), 0)
