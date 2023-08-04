from typing import Type

from jarvis_db.factories.services import create_user_service, create_account_service, create_token_service, \
    create_economy_service, create_frequency_service, create_marketplace_service
from jorm.jarvis.db_update import UserInfoChanger, JORMChanger
from sqlalchemy.orm import Session

from jdu.db_tools.fill.wildberries_fillers import WildberriesDBFillerImpl
from jdu.db_tools.update.jorm_changer_impl import JORMChangerImpl
from jdu.db_tools.update.user_info_changer import UserInfoChangerImpl
from jdu.providers.initializers import DataProviderInitializer
from jdu.providers.providers import UserMarketDataProvider
from jdu.providers.wildberries_providers import WildberriesDataProviderWithoutKey, \
    WildberriesDataProviderWithoutKeyImpl, WildberriesUserMarketDataProviderImpl
from tests.basic_db_test import AUTH_KEY
from tests.initializers.wildberries_initializer import WildberriesTestDBFillerInitializer, \
    WildberriesTestDataProviderInitializer
from tests.providers.wildberries_test_provider import WildBerriesDataProviderWithoutKeyImplTest, \
    WildberriesUserMarketDataProviderImplTest

__TEST_PROVIDER_INITIALIZER_MAP: dict[str, tuple[Type[UserMarketDataProvider], Type[DataProviderInitializer]]] = {
    'wildberries': (WildberriesUserMarketDataProviderImplTest, WildberriesTestDataProviderInitializer)
}


def create_user_info_changer(session: Session) -> UserInfoChanger:
    user_service = create_user_service(session)
    account_service = create_account_service(session)
    token_service = create_token_service(session)
    return UserInfoChangerImpl(user_service, account_service, token_service)


def create_jorm_changer(session: Session) -> JORMChanger:
    economy_service = create_economy_service(session)
    frequency_service = create_frequency_service(session)
    user_service = create_user_service(session)
    marketplace_service = create_marketplace_service(session)
    db_filler = create_wb_db_filler(session)
    return JORMChangerImpl(
        economy_service=economy_service,
        frequency_service=frequency_service,
        user_service=user_service,
        marketplace_service=marketplace_service,
        db_filler=db_filler,
        provider_initializing_mapping=__TEST_PROVIDER_INITIALIZER_MAP
    )


def create_real_wb_db_filler(session: Session) -> WildberriesDBFillerImpl:
    return WildberriesDBFillerImpl(session,
                                   create_wb_data_provider_without_key(),
                                   WildberriesTestDBFillerInitializer)


def create_wb_db_filler(session: Session) -> WildberriesDBFillerImpl:
    return WildberriesDBFillerImpl(session,
                                   WildBerriesDataProviderWithoutKeyImplTest(WildberriesTestDataProviderInitializer),
                                   WildberriesTestDBFillerInitializer)


def create_wb_data_provider_without_key() -> WildberriesDataProviderWithoutKey:
    return WildberriesDataProviderWithoutKeyImpl(WildberriesTestDataProviderInitializer)


def create_wb_data_provider_with_key() -> WildberriesUserMarketDataProviderImpl:
    return WildberriesUserMarketDataProviderImpl(AUTH_KEY, WildberriesTestDataProviderInitializer)
