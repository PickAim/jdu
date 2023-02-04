from abc import ABC
from abc import abstractmethod
from sqlalchemy.orm import Session
from jdu.providers.common import WildBerriesDataProvider
from jorm.market.infrastructure import Category
from jarvis_db.repositores.market.infrastructure import CategoryRepository


class DBFiller(ABC):
    pass


class WildberriesDbFiller(DBFiller):
    @abstractmethod
    def fill_categories(self):
        pass

    @abstractmethod
    def fill_niches(self):
        pass

    @abstractmethod
    def fill_niche_products(self, niche: str, pages: int = 1):
        pass

    @abstractmethod
    def fill_niche_price_history(self, niche: str):
        pass


class SyncWildberriesDBFiller(WildberriesDbFiller):

    def __init__(self, provider: WildBerriesDataProvider, session: Session):
        self.__provider = provider
        self.__session = session

    def fill_categories(self):
        category_names = self.__provider.get_categories()
        repository = CategoryRepository(self.__session)
        categories = [Category(name, []) for name in category_names]
        for category in categories:
            repository.add(category)

    def fill_niches(self):
        # TODO Not implemented
        pass

    def fill_niche_products(self, niche: str, pages: int = 1):
        # TODO Not implemented
        pass

    def fill_niche_price_history(self, niche: str):
        # TODO Not implemented
        pass
