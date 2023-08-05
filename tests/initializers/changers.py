from jarvis_db.factories.services import create_economy_service, create_frequency_service, create_user_service, \
    create_marketplace_service, create_warehouse_service, create_category_service, create_niche_service, \
    create_product_card_service
from sqlalchemy.orm import Session

from jdu.db_tools.fill.db_fillers_impl import StandardDBFillerImpl
from jdu.db_tools.update.jorm.base import JORMChangerBase, InitInfo
from jdu.db_tools.update.jorm.initializers import JORMChangerInitializer
from tests.initializers.wildberries_initializer import WildberriesTestDataProviderInitializer, \
    WildberriesTestDBFillerInitializer
from tests.providers.wildberries_test_provider import WildberriesUserMarketDataProviderImplTest, \
    WildberriesDataProviderWithoutKeyImplTest

TEST_PROVIDER_INITIALIZER_MAP: dict[str, InitInfo] = {
    'wildberries': InitInfo(WildberriesUserMarketDataProviderImplTest,
                            WildberriesDataProviderWithoutKeyImplTest,
                            StandardDBFillerImpl,
                            WildberriesTestDataProviderInitializer,
                            WildberriesTestDBFillerInitializer)
}


class JORMChangerInitializerTestImpl(JORMChangerInitializer):
    @staticmethod
    def init_jorm_changer(session: Session, jorm_changer: JORMChangerBase):
        jorm_changer.economy_service = create_economy_service(session)
        jorm_changer.frequency_service = create_frequency_service(session)
        jorm_changer.user_service = create_user_service(session)
        jorm_changer.marketplace_service = create_marketplace_service(session)
        jorm_changer.warehouse_service = create_warehouse_service(session)
        jorm_changer.category_service = create_category_service(session)
        jorm_changer.niche_service = create_niche_service(session)
        jorm_changer.product_card_service = create_product_card_service(session)
        jorm_changer.initializing_mapping = TEST_PROVIDER_INITIALIZER_MAP
