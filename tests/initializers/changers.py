from jarvis_db.factories.services import create_economy_service, create_frequency_service, create_user_service, \
    create_marketplace_service, create_warehouse_service, create_category_service, create_niche_service, \
    create_token_service, create_account_service, create_product_card_service

from jdu.db_tools.fill.db_fillers_impl import StandardDBFillerImpl
from jdu.db_tools.update.jorm.base import JORMChangerBase, InitInfo
from jdu.db_tools.update.jorm.initializers import JORMChangerInitializer
from jdu.db_tools.update.user.base import UserInfoChangerBase
from jdu.db_tools.update.user.initializers import UserInfoChangerInitializer
from jdu.support.constant import WILDBERRIES_NAME
from tests.initializers.wildberries_initializer import TestWildberriesDataProviderInitializer, \
    TestWildberriesDBFillerInitializer
from tests.providers.wildberries_test_provider import TestWildberriesUserMarketDataProviderImpl, \
    TestWildberriesDataProviderWithoutKeyImpl

TEST_PROVIDER_INITIALIZER_MAP: dict[str, InitInfo] = {
    WILDBERRIES_NAME: InitInfo(TestWildberriesUserMarketDataProviderImpl,
                               TestWildberriesDataProviderWithoutKeyImpl,
                               StandardDBFillerImpl,
                               TestWildberriesDataProviderInitializer,
                               TestWildberriesDBFillerInitializer)
}


class JORMChangerInitializerTestImpl(JORMChangerInitializer):
    def _init_something(self, jorm_changer: JORMChangerBase):
        session = self.session
        jorm_changer.economy_service = create_economy_service(session)
        jorm_changer.frequency_service = create_frequency_service(session)
        jorm_changer.user_service = create_user_service(session)
        jorm_changer.marketplace_service = create_marketplace_service(session)
        jorm_changer.warehouse_service = create_warehouse_service(session)
        jorm_changer.category_service = create_category_service(session)
        jorm_changer.niche_service = create_niche_service(session)
        jorm_changer.product_card_service = create_product_card_service(session)
        jorm_changer.initializing_mapping = TEST_PROVIDER_INITIALIZER_MAP


class UserInfoChangerInitializerImpl(UserInfoChangerInitializer):
    def _init_something(self, jorm_changer: UserInfoChangerBase):
        session = self.session
        jorm_changer.user_service = create_user_service(session)
        jorm_changer.token_service = create_token_service(session)
        jorm_changer.account_service = create_account_service(session)
