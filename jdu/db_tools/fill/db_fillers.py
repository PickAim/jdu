from abc import ABC
from abc import abstractmethod
from typing import Type

from jorm.market.infrastructure import Niche, Marketplace, Warehouse, Address, HandlerType
from jorm.support.constants import DEFAULT_WAREHOUSE_NAME
from sqlalchemy.orm import Session

from jdu.db_tools.fill.base import DBFiller
from jdu.db_tools.fill.initializers import DBFillerInitializer
from jdu.providers.providers import UserMarketDataProvider


class __InitializableDBFiller(DBFiller):
    def __init__(self, session: Session, db_initializer_class: Type[DBFillerInitializer]):
        super().__init__()
        db_initializer_class().init_db_filler(session, self)
        self.__try_to_init_marketplace_in_db()
        self.__try_to_init_default_warehouse()

    def __try_to_init_marketplace_in_db(self):
        if not self.marketplace_service.exists_with_name(self.marketplace_name):
            self.marketplace_service.create(Marketplace(self.marketplace_name))
        self.marketplace_id = self.marketplace_service.find_by_name(self.marketplace_name)[1]

    def __try_to_init_default_warehouse(self):
        default_warehouse = Warehouse(DEFAULT_WAREHOUSE_NAME, 1, HandlerType.MARKETPLACE, Address())
        if self.warehouse_service.find_by_global_id(self.marketplace_id, 1) is None:
            self.warehouse_service.create_warehouse(default_warehouse, self.marketplace_id)


class SimpleDBFiller(__InitializableDBFiller):
    pass


class StandardDBFiller(__InitializableDBFiller, ABC):
    @abstractmethod
    def fill_categories(self, category_num: int = -1) -> None:
        pass

    @abstractmethod
    def fill_niche_by_name(self, niche_name: str, product_num: int = -1) -> Niche | None:
        pass

    @abstractmethod
    def fill_niches(self, niche_num: int = -1) -> None:
        pass

    @abstractmethod
    def fill_products(self, products_count: int = -1) -> None:
        pass
    
    @abstractmethod
    def fill_warehouse(self, provider_with_key: UserMarketDataProvider) -> list[Warehouse]:
        pass
