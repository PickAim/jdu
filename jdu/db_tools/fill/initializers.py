from abc import ABC, abstractmethod

from jdu.db_tools.fill.base import DBFiller


class DBFillerInitializer(ABC):
    def init_db_filler(self, db_filler_to_init: DBFiller):
        db_filler_to_init.marketplace_name = self.get_marketplace_name()

    @abstractmethod
    def get_marketplace_name(self) -> str:
        return 'default'
