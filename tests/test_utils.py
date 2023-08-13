from jarvis_db.factories.services import create_user_service, create_account_service, create_token_service, \
    create_marketplace_service, create_warehouse_service
from jorm.jarvis.db_update import UserInfoChanger, JORMChanger
from sqlalchemy.orm import Session

from jdu.db_tools.fill.db_fillers_impl import StandardDBFillerImpl
from jdu.db_tools.update.jorm.jorm_changer_impl import JORMChangerImpl
from jdu.db_tools.update.user_info_changer import UserInfoChangerImpl
from jdu.providers.wildberries_providers import WildberriesDataProviderWithoutKey, \
    WildberriesDataProviderWithoutKeyImpl, WildberriesUserMarketDataProviderImpl
from tests.basic_db_test import AUTH_KEY
from tests.initializers.changers import JORMChangerInitializerTestImpl
from tests.initializers.wildberries_initializer import TestWildberriesDBFillerInitializer, \
    TestWildberriesDataProviderInitializer
from tests.providers.wildberries_test_provider import TestWildberriesDataProviderWithoutKeyImpl


def create_user_info_changer(session: Session) -> UserInfoChanger:
    user_service = create_user_service(session)
    account_service = create_account_service(session)
    token_service = create_token_service(session)
    return UserInfoChangerImpl(user_service, account_service, token_service)


def create_jorm_changer(session: Session) -> JORMChanger:
    return JORMChangerImpl(session, JORMChangerInitializerTestImpl)


def create_real_wb_db_filler(session: Session) -> StandardDBFillerImpl:
    return StandardDBFillerImpl(create_marketplace_service(session),
                                create_warehouse_service(session),
                                TestWildberriesDBFillerInitializer)


def create_wb_db_filler(session: Session) -> StandardDBFillerImpl:
    return StandardDBFillerImpl(create_marketplace_service(session),
                                create_warehouse_service(session),
                                TestWildberriesDBFillerInitializer)


def create_wb_real_data_provider_without_key() -> WildberriesDataProviderWithoutKey:
    return WildberriesDataProviderWithoutKeyImpl(TestWildberriesDataProviderInitializer)


def create_wb_data_provider_without_key() -> WildberriesDataProviderWithoutKey:
    return TestWildberriesDataProviderWithoutKeyImpl(TestWildberriesDataProviderInitializer)


def create_wb__real_data_provider_with_key() -> WildberriesUserMarketDataProviderImpl:
    return WildberriesUserMarketDataProviderImpl(AUTH_KEY, TestWildberriesDataProviderInitializer)
