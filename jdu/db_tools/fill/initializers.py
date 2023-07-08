from abc import ABC, abstractmethod

from jdu.db_tools.fill.base import DBFiller
from sqlalchemy.orm import Session


class DBFillerInitializer(ABC):
    def init_db_filler(self, session: Session, db_filler_to_init: DBFiller):
        db_filler_to_init.marketplace_name = self.get_marketplace_name()
        self.additional_init_db_filler(session, db_filler_to_init)

    @abstractmethod
    def additional_init_db_filler(self, session: Session, db_filler_to_init: DBFiller):
        return

    @abstractmethod
    def get_marketplace_name(self) -> str:
        return 'default'
