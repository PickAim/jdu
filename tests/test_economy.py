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
from jarvis_db.tables import Marketplace, Category, Niche, Account, User, Warehouse, Address
from jorm.market.service import RequestInfo, UnitEconomyRequest, UnitEconomyResult
from sqlalchemy.orm import Session

from jdu.db_tools.update.jorm_changer_impl import JormChangerImpl
from tests.db_context import DbContext


class AccountServiceTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext()
        with self.__db_context.session() as session, session.begin():
            marketplace = Marketplace(name="qwerty")
            self.__category_name = "qwerty"
            category = Category(name=self.__category_name, marketplace=marketplace)
            self.__niche_name = "niche#1"
            niche = Niche(
                name=self.__niche_name,
                marketplace_commission=1,
                partial_client_commission=1,
                client_commission=1,
                return_percent=1,
                category=category,
            )
            account = Account(phone="", email="", password="")
            user = User(name="", profit_tax=1, account=account)
            address = Address(
                country="AS", region="QS", street="DD", number="HH", corpus="YU"
            )
            warehouse = Warehouse(
                owner=marketplace,
                global_id=200,
                type=0,
                name="qwerty",
                address=address,
                basic_logistic_to_customer_commission=0,
                additional_logistic_to_customer_commission=0,
                logistic_from_customer_commission=0,
                basic_storage_commission=0,
                additional_storage_commission=0,
                monopalette_storage_commission=0,
            )
            session.add(user)
            session.add(niche)
            session.add(warehouse)
            session.flush()
            self.__niche_id = niche.id
            self.__user_id = user.id
            self.__marketplace_id = marketplace.id
            self.__warehouse_id = warehouse.id
            self.__warehouse_name = warehouse.name

    def test_change_unit_economy(self):
        request_info = RequestInfo(date=datetime(2020, 10, 23), name="name")
        request_entity = UnitEconomyRequest(
            100,
            20,
            self.__niche_name,
            self.__category_name,
            11,
            121,
            33,
            warehouse_name="qwerty",
        )
        result = UnitEconomyResult(200, 300, 12, 25, 151, 134, 12355, 2, 1.2, 2.0)
        with self.__db_context.session() as session, session.begin():
            wildberries_changer = JormChangerImpl(create_economy_service(session),
                                                  create_frequence_service(session))
            wildberries_changer.save_unit_economy_request(request_entity,
                                                          result,
                                                          request_info,
                                                          self.__user_id,
                                                          self.__marketplace_id)
        with self.__db_context.session() as session:
            service = create_economy_service(session)
            # TODO how to get the result?


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


def create_frequence_service(session: Session) -> FrequencyService:
    return FrequencyService(
        FrequencyRequestRepository(session),
        FrequencyResultRepository(session),
        FrequencyRequestTableToJormMapper(),
    )
