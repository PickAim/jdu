from jarvis_db.factories.services import create_user_service, create_account_service, create_token_service
from jorm.jarvis.db_update import UserInfoChanger
from sqlalchemy.orm import Session

from jdu.db_tools.fill.wildberries_fillers import WildberriesDBFillerImpl
from jdu.db_tools.update.user_info_changer import UserInfoChangerImpl
from jdu.providers.wildberries_providers import WildberriesDataProviderWithoutKey, \
    WildberriesDataProviderWithoutKeyImpl, WildberriesUserMarketDataProviderImpl
from tests.basic_db_test import AUTH_KEY
from tests.initializers.wildberries_initializer import WildberriesTestDBFillerInitializer, \
    WildberriesTestDataProviderInitializer
from tests.providers.wildberries_test_provider import WildBerriesDataProviderWithoutKeyImplTest


def create_user_info_changer(session: Session) -> UserInfoChanger:
    user_service = create_user_service(session)
    account_service = create_account_service(session)
    token_service = create_token_service(session)
    return UserInfoChangerImpl(user_service, account_service, token_service)


def create_wb_db_filler(session: Session) -> WildberriesDBFillerImpl:
    return WildberriesDBFillerImpl(session,
                                   WildBerriesDataProviderWithoutKeyImplTest(WildberriesTestDataProviderInitializer),
                                   WildberriesTestDBFillerInitializer)


def create_wb_data_provider_without_key() -> WildberriesDataProviderWithoutKey:
    return WildberriesDataProviderWithoutKeyImpl(WildberriesTestDataProviderInitializer)


def create_wb_data_provider_with_key() -> WildberriesUserMarketDataProviderImpl:
    return WildberriesUserMarketDataProviderImpl(AUTH_KEY, WildberriesTestDataProviderInitializer)
