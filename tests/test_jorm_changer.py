import unittest
from datetime import datetime

from jarvis_db.factories.services import create_economy_service
from jarvis_db.factories.services import create_warehouse_service
from jorm.market.service import RequestInfo, UnitEconomyRequest, UnitEconomyResult

from tests.basic_db_test import TestDBContextAdditions, BasicDBTest
from tests.test_utils import create_jorm_changer


class JORMChangerTest(BasicDBTest):
    @classmethod
    def get_db_init_flags_for_tests(cls) -> dict[str, list[TestDBContextAdditions]]:
        return {
            'test_fill_warehouses': [TestDBContextAdditions.USER_API_KEY],
            'test_unit_economy_request_changes': [TestDBContextAdditions.NICHE,
                                                  TestDBContextAdditions.WAREHOUSES,
                                                  TestDBContextAdditions.USER]
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

    def test_unit_economy_request_changes(self):
        # region RequestInfo create
        date_to_save = datetime(2020, 10, 23)
        request_name_to_save = "request name"
        request_info = RequestInfo(date=date_to_save, name=request_name_to_save)
        # endregion
        # region UnitEconomyRequest create
        buy_cost_to_save = 100
        pack_cost_to_save = 50
        transit_count_to_save = 11
        transit_price_to_save = 121
        market_place_transit_price_to_save = 33
        request_entity = UnitEconomyRequest(
            self.test_niche_name,
            self.category_id,
            self.marketplace_id,
            buy=buy_cost_to_save,
            pack=pack_cost_to_save,
            transit_count=transit_count_to_save,
            transit_price=transit_price_to_save,
            market_place_transit_price=market_place_transit_price_to_save,
            warehouse_name=self.test_warehouse_name,
        )
        # endregion
        # region UnitEconomyResult create
        product_cost_to_save = 200
        pack_cost_to_save = 300
        marketplace_commission_to_save = 12
        logistic_price_to_save = 25
        storage_price_to_save = 151
        margin_to_save = 134
        recommended_price_to_save = 12355
        transit_profit_to_save = 2
        roi_to_save = 1.2
        transit_margin_to_save = 2.0
        result_entity = UnitEconomyResult(
            product_cost=product_cost_to_save,
            pack_cost=pack_cost_to_save,
            marketplace_commission=marketplace_commission_to_save,
            logistic_price=logistic_price_to_save,
            storage_price=storage_price_to_save,
            margin=margin_to_save,
            recommended_price=recommended_price_to_save,
            transit_profit=transit_profit_to_save,
            roi=roi_to_save,
            transit_margin=transit_margin_to_save
        )
        # endregion
        with self.db_context.session() as session, session.begin():
            wildberries_changer = create_jorm_changer(session)
            wildberries_changer.save_unit_economy_request(request_entity, result_entity, request_info, self.user_id)

        request_id = 1
        with self.db_context.session() as session:
            service = create_economy_service(session)
            id_to_saved_request = service.find_user_requests(self.user_id)
            self.assertEqual(len(id_to_saved_request), 1)
            self.assertTrue(request_id in id_to_saved_request)
            saved_request, saved_result, saved_info = id_to_saved_request[1]

            self.assertEqual(request_info.date, saved_info.date)
            self.assertEqual(request_id, saved_info.id)
            self.assertEqual(request_info.name, saved_info.name)

            self.assertEqual(request_entity.buy, saved_request.buy)
            self.assertEqual(request_entity.pack, saved_request.pack)
            self.assertEqual(request_entity.marketplace_id, saved_request.marketplace_id)
            self.assertEqual(request_entity.category_id, saved_request.category_id)
            self.assertEqual(request_entity.niche, saved_request.niche)
            self.assertEqual(request_entity.warehouse_name, saved_request.warehouse_name)
            self.assertEqual(request_entity.market_place_transit_price, saved_request.market_place_transit_price)
            self.assertEqual(request_entity.transit_price, saved_request.transit_price)
            self.assertEqual(request_entity.transit_count, saved_request.transit_count)

            self.assertEqual(result_entity.product_cost, saved_result.product_cost)
            self.assertEqual(result_entity.pack_cost, saved_result.pack_cost)
            self.assertEqual(result_entity.marketplace_commission, saved_result.marketplace_commission)
            self.assertEqual(result_entity.logistic_price, saved_result.logistic_price)
            self.assertEqual(result_entity.storage_price, saved_result.storage_price)
            self.assertEqual(result_entity.margin, saved_result.margin)
            self.assertEqual(result_entity.recommended_price, saved_result.recommended_price)
            self.assertEqual(result_entity.transit_profit, saved_result.transit_profit)
            self.assertEqual(result_entity.roi, saved_result.roi)
            self.assertEqual(result_entity.transit_margin, saved_result.transit_margin)

        with self.db_context.session() as session, session.begin():
            wildberries_changer = create_jorm_changer(session)
            wildberries_changer.delete_unit_economy_request(request_id, self.user_id)
        with self.db_context.session() as session:
            service = create_economy_service(session)
            db_economy = service.find_user_requests(1)
            self.assertEqual(len(db_economy), 0)


if __name__ == '__main__':
    unittest.main()
