from datetime import datetime

from jarvis_db.factories.services import create_economy_service
from jorm.market.service import RequestInfo, UnitEconomyRequest, UnitEconomyResult

from tests.basic_db_test import BasicDBTest, TestDBContextAdditions
from tests.test_utils import create_jorm_changer


class AccountServiceTest(BasicDBTest):
    @classmethod
    def get_db_init_flags_for_tests(cls) -> dict[str, list[TestDBContextAdditions]]:
        return {
            'test_change_unit_economy': [TestDBContextAdditions.NICHE,
                                         TestDBContextAdditions.WAREHOUSES,
                                         TestDBContextAdditions.USER],
            'test_remove_unit_economy': [TestDBContextAdditions.NICHE,
                                         TestDBContextAdditions.WAREHOUSES,
                                         TestDBContextAdditions.USER]
        }

    def test_change_unit_economy(self):
        request_info = RequestInfo(date=datetime(2020, 10, 23), name="name")
        request_entity = UnitEconomyRequest(
            self.test_niche_name,
            self.category_id,
            self.marketplace_id,
            100,
            50,
            transit_count=11,
            transit_price=121,
            market_place_transit_price=33,
            warehouse_name=self.test_warehouse_name,
        )
        result = UnitEconomyResult(200, 300, 12, 25, 151, 134, 12355, 2, 1.2, 2.0)
        with self.db_context.session() as session, session.begin():
            wildberries_changer = create_jorm_changer(session)
            wildberries_changer.save_unit_economy_request(request_entity,
                                                          result,
                                                          request_info,
                                                          self.user_id)
        with self.db_context.session() as session:
            service = create_economy_service(session)
            db_economy = service.find_user_requests(self.user_id)
            self.assertEqual(len(db_economy), 1)

    def test_remove_unit_economy(self):
        request_id = 1
        result_id = 1
        with self.db_context.session() as session, session.begin():
            wildberries_changer = create_jorm_changer(session)
            wildberries_changer.delete_unit_economy_request(request_id, result_id)
        with self.db_context.session() as session:
            service = create_economy_service(session)
            db_economy = service.find_user_requests(1)
            self.assertEqual(len(db_economy), 0)
