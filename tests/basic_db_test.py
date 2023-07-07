import abc
import inspect
import unittest
from enum import IntEnum
from typing import Callable

from jarvis_db.repositores.mappers.market.infrastructure import CategoryTableToJormMapper, NicheTableToJormMapper, \
    MarketplaceTableToJormMapper, WarehouseTableToJormMapper
from jarvis_db.repositores.mappers.market.items import ProductTableToJormMapper
from jarvis_db.repositores.mappers.market.person import UserTableToJormMapper, AccountTableToJormMapper
from jarvis_db.repositores.market.infrastructure import CategoryRepository, MarketplaceRepository, NicheRepository, \
    WarehouseRepository
from jarvis_db.repositores.market.items import ProductCardRepository
from jarvis_db.repositores.market.person import UserRepository, AccountRepository
from jarvis_db.services.market.infrastructure.category_service import CategoryService
from jarvis_db.services.market.infrastructure.marketplace_service import MarketplaceService
from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.services.market.infrastructure.warehouse_service import WarehouseService
from jarvis_db.services.market.items.product_card_service import ProductCardService
from jarvis_db.services.market.person import UserService, AccountService
from jorm.market.infrastructure import Marketplace, Warehouse, HandlerType, Category, Niche, Address
from jorm.market.items import Product
from jorm.market.person import Account, User
from sqlalchemy.orm import Session

from tests.db_context import DbContext


class TestDBContextAdditions(IntEnum):
    MARKETPLACE = 0
    CATEGORY = 1
    NICHE = 2
    PRODUCT = 3
    WAREHOUSE = 4
    USER = 5


def __create_test_warehouse() -> Warehouse:
    address = __create_test_address()
    warehouse = Warehouse(
        BasicDBTest.test_warehouse_name,
        200,
        HandlerType.MARKETPLACE,
        address,
        basic_logistic_to_customer_commission=0,
        additional_logistic_to_customer_commission=0,
        logistic_from_customer_commission=0,
        basic_storage_commission=0,
        additional_storage_commission=0,
        mono_palette_storage_commission=0
    )
    return warehouse


def __add_warehouse(session: Session) -> int:
    marketplace_id = __add_marketplace(session)
    warehouse = __create_test_warehouse()
    service = WarehouseService(WarehouseRepository(session), WarehouseTableToJormMapper())
    found_info = service.find_warehouse_by_name(warehouse.name)
    if found_info is None:
        service.create_warehouse(warehouse, marketplace_id)
        found_info = service.find_warehouse_by_name(warehouse.name)
    return found_info[1]


def __create_test_niche() -> Niche:
    niche = Niche(
        BasicDBTest.test_niche_name,
        {
            HandlerType.MARKETPLACE: 0,
            HandlerType.CLIENT: 0,
            HandlerType.PARTIAL_CLIENT: 0
        },
        0.1
    )
    return niche


def __add_niche(session: Session) -> int:
    category_id = __add_category(session)
    niche = __create_test_niche()
    service = NicheService(NicheRepository(session), NicheTableToJormMapper())
    found_info = service.find_by_name(niche.name, category_id)
    if found_info is None:
        service.create(niche, category_id)
        found_info = service.find_by_name(niche.name, category_id)
    return found_info[1]


def __create_test_category() -> Category:
    return Category(BasicDBTest.test_category_name)


def __add_category(session: Session):
    marketplace_id = __add_marketplace(session)
    category = __create_test_category()
    service = CategoryService(CategoryRepository(session),
                              CategoryTableToJormMapper(NicheTableToJormMapper()))
    found_info = service.find_by_name(category.name, marketplace_id)
    if found_info is None:
        service.create(category, marketplace_id)
        found_info = service.find_by_name(category.name, marketplace_id)
    return found_info[1]


def __create_test_user() -> User:
    return User(user_id=BasicDBTest.user_id)


def __add_user(session: Session) -> int:
    account_id = __add_account(session)
    user = __create_test_user()
    service = UserService(UserRepository(session), UserTableToJormMapper())
    try:
        found_info = service.find_by_id(user.user_id)
    except Exception:
        service.create(user, account_id)
    return user.user_id


def __create_test_account() -> Account:
    return Account(BasicDBTest.test_user_email, BasicDBTest.test_user_password, BasicDBTest.test_user_phone)


def __add_account(session: Session) -> int:
    account = __create_test_account()
    service = AccountService(AccountRepository(session), AccountTableToJormMapper())
    found_info = service.find_by_email_or_phone(account.email, account.phone_number)
    if found_info is None:
        service.create(account)
        found_info = service.find_by_email_or_phone(account.email, account.phone_number)
    return found_info[1]


def __create_test_marketplace() -> Marketplace:
    return Marketplace("wildberries")


def __add_marketplace(session: Session) -> int:
    marketplace = __create_test_marketplace()
    service = MarketplaceService(MarketplaceRepository(session),
                                 MarketplaceTableToJormMapper(WarehouseTableToJormMapper()))
    found_info = service.find_by_name(marketplace.name)
    if found_info is None:
        service.create(marketplace)
        found_info = service.find_by_name(marketplace.name)
    return found_info[1]


def __create_test_address() -> Address:
    return Address()


def __create_test_product() -> Product:
    return Product(
        BasicDBTest.test_product_name,
        10,
        1,
        1.0,
        BasicDBTest.test_product_brand,
        BasicDBTest.test_product_seller,
        BasicDBTest.test_niche_name,
        BasicDBTest.test_category_name
    )


def __add_product(session: Session) -> int:
    niche_id = __add_niche(session)
    product = __create_test_product()
    service = ProductCardService(ProductCardRepository(session), ProductTableToJormMapper())
    found_info = service.find_all_in_niche(niche_id)
    if len(found_info) == 0:
        service.create_product(product, niche_id)
    return product.global_id


_CREATE_TEST_OBJECT_METHODS: dict[TestDBContextAdditions, Callable[[Session], int]] = {
    TestDBContextAdditions.MARKETPLACE: __add_marketplace,
    TestDBContextAdditions.CATEGORY: __add_category,
    TestDBContextAdditions.NICHE: __add_niche,
    TestDBContextAdditions.PRODUCT: __add_product,
    TestDBContextAdditions.WAREHOUSE: __add_warehouse,
    TestDBContextAdditions.USER: __add_user,
}


class BasicDBTest(unittest.TestCase):
    niche_id = 1
    user_id = 1
    marketplace_id = 1
    category_id = 1
    product_id = 1
    warehouse_id = 1
    warehouse_name = 1

    test_category_name = "category"
    test_niche_name = "niche"
    test_warehouse_name = "warehouse"
    test_product_name = "product"
    test_product_brand = "brand"
    test_product_seller = "seller"

    test_user_email = "ddd@ddmm.com"
    test_user_phone = "+777777777"
    test_user_password = "123!Hashed"

    @classmethod
    def setUpClass(cls) -> None:
        cls.addition_flags_for_tests = cls.get_db_init_flags_for_tests()

    def setUp(self):
        self.db_context = DbContext()
        frame = inspect.currentframe()
        test_name = inspect.getargvalues(frame).locals['self']._testMethodName
        if test_name not in self.addition_flags_for_tests:
            return
        addition_flags = self.addition_flags_for_tests[test_name]
        with self.db_context.session() as session, session.begin():
            for flag in addition_flags:
                _CREATE_TEST_OBJECT_METHODS[flag](session)
            session.flush()

    @classmethod
    @abc.abstractmethod
    def get_db_init_flags_for_tests(cls) -> dict[str, list[TestDBContextAdditions]]:
        pass
