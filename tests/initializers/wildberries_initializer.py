from jarvis_db.factories.services import create_marketplace_service, create_category_service, create_niche_service, \
    create_warehouse_service, create_product_history_service, create_product_card_service
from sqlalchemy.orm import Session

from jdu.db_tools.fill.base import DBFiller
from jdu.db_tools.fill.initializers import DBFillerInitializer


class WildberriesTestDBFillerInitializer(DBFillerInitializer):
    WILDBERRIES_NAME = 'wildberries'

    def get_marketplace_name(self) -> str:
        return self.WILDBERRIES_NAME

    def additional_init_db_filler(self, session: Session, db_filler: DBFiller):
        db_filler.marketplace_service = create_marketplace_service(session)
        db_filler.category_service = create_category_service(session)
        db_filler.niche_service = create_niche_service(session)

        db_filler.product_service = create_product_card_service(session)
        db_filler.warehouse_service = create_warehouse_service(session)
        db_filler.product_history_service = create_product_history_service(session)
