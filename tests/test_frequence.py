import unittest
from datetime import datetime

from jarvis_db.repositores.mappers.market.infrastructure import NicheTableToJormMapper, CategoryTableToJormMapper, \
    WarehouseTableToJormMapper
from jarvis_db.repositores.mappers.market.service import EconomyResultTableToJormMapper, \
    EconomyRequestTableToJormMapper, FrequencyRequestTableToJormMapper
from jarvis_db.repositores.market.infrastructure import CategoryRepository, NicheRepository, WarehouseRepository
from jarvis_db.repositores.market.service import EconomyRequestRepository, EconomyResultRepository, \
    FrequencyRequestRepository, FrequencyResultRepository
from jarvis_db.services.market.infrastructure.category_service import CategoryService
from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.services.market.infrastructure.warehouse_service import WarehouseService
from jarvis_db.services.market.service.economy_service import EconomyService
from jarvis_db.services.market.service.frequency_service import FrequencyService
from jarvis_db.tables import Account, User
from jorm.market.service import RequestInfo, FrequencyRequest, FrequencyResult
from sqlalchemy.orm import Session

from jdu.db_tools.update.jorm_changer_impl import JormChangerImpl
from tests.db_context import DbContext


class FrequencyRequestTest(unittest.TestCase):
    def setUp(self) -> None:
        self.__db_context = DbContext()
        with self.__db_context.session() as session, session.begin():
            account = Account(phone="", email="", password="")
            user = User(name="", profit_tax=1, account=account)
            session.add(user)
            session.flush()
            self.__user_id = user.id

    def test_change_frequency(self):
        request_info = RequestInfo(date=datetime(2020, 2, 2), name="name")
        request = FrequencyRequest("search")
        result = FrequencyResult({i: i + 1 for i in range(10)})
        with self.__db_context.session() as session, session.begin():
            wildberries_changer = JormChangerImpl(create_economy_service(session),
                                                  create_frequency_service(session))
            wildberries_changer.save_frequency_request(request,
                                                       result,
                                                       request_info,
                                                       self.__user_id
                                                       )
        with self.__db_context.session() as session:
            service = create_frequency_service(session)
            db_economy = service.find_user_requests(1)
            self.assertEqual(len(db_economy), 1)

    def test_remove_frequency(self):
        request_id = 1
        result_id = 1
        with self.__db_context.session() as session, session.begin():
            wildberries_changer = JormChangerImpl(create_economy_service(session),
                                                  create_frequency_service(session))
            wildberries_changer.delete_frequency_request(request_id, result_id)
        with self.__db_context.session() as session:
            service = create_frequency_service(session)
            db_economy = service.find_user_requests(1)
            self.assertEqual(len(db_economy), 0)


def create_economy_service(session: Session) -> EconomyService:
    niche_mapper = NicheTableToJormMapper()
    return EconomyService(
        EconomyRequestRepository(session),
        EconomyResultRepository(session),
        EconomyResultTableToJormMapper(EconomyRequestTableToJormMapper()),
        CategoryService(
            CategoryRepository(session),
            CategoryTableToJormMapper(niche_mapper),
        ),
        NicheService(NicheRepository(session), niche_mapper),
        WarehouseService(WarehouseRepository(session), WarehouseTableToJormMapper()),
    )


def create_frequency_service(session: Session) -> FrequencyService:
    return FrequencyService(
        FrequencyRequestRepository(session),
        FrequencyResultRepository(session),
        FrequencyRequestTableToJormMapper(),
    )
