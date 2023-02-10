from abc import ABC
from abc import abstractmethod

from jarvis_db.repositores.mappers.market.infrastructure import CategoryTableToJormMapper, NicheTableToJormMapper, \
    NicheJormToTableMapper, CategoryJormToTableMapper
from jarvis_db.repositores.mappers.market.items import ProductTableToJormMapper, ProductJormToTableMapper
from jarvis_db.repositores.market.infrastructure import CategoryRepository, NicheRepository
from jarvis_db.repositores.market.items import ProductCardRepository
from jorm.market.infrastructure import Category, Niche
from jorm.market.items import Product
from sqlalchemy.orm import Session

from jdu.providers.common import WildBerriesDataProviderWithoutKey


class DBFiller(ABC):
    def __init__(self):
        self.marketplace_name: str = 'default'


class WildberriesDbFiller(DBFiller):

    @abstractmethod
    def fill_categories(self):
        pass

    @abstractmethod
    def fill_niches(self):
        pass

    @abstractmethod
    def fill_niche_products(self):
        pass

    @abstractmethod
    def fill_niche_price_history(self, niche: str):
        pass


class WildberriesDBFillerImpl(WildberriesDbFiller):

    def __init__(self, provider: WildBerriesDataProviderWithoutKey, session: Session):
        super().__init__()
        self.marketplace_name = 'wildberries'
        self.__provider = provider
        self.__session = session

    def fill_categories(self):
        categories: list[Category] = self.__provider.get_categories(1, 1, 1)
        repository = CategoryRepository(
            self.__session, CategoryTableToJormMapper(NicheTableToJormMapper()),
            CategoryJormToTableMapper(NicheJormToTableMapper()))
        repository.add_all_categories_to_marketplace(categories, self.marketplace_name)

    def fill_niches(self):
        categories: list[Category] = self.__provider.get_categories(1, 1, 1)
        repository = NicheRepository(
            self.__session, NicheTableToJormMapper(), NicheJormToTableMapper())
        for category in categories:
            niches = self.__provider.get_niches_by_category(category.name, 1, 1)
            repository.add_all_by_category_name(niches, category.name, self.marketplace_name)

    def fill_niche_products(self):
        repository = ProductCardRepository(
            self.__session, ProductTableToJormMapper(), ProductJormToTableMapper())
        categories: list[Category] = self.__provider.get_categories(1, 1, 1)
        for category in categories:
            niches: list[Niche] = self.__provider.get_niches_by_category(category.name, 1, 1)
            for niche in niches:
                products: list[Product] = self.__provider.get_products_by_niche(niche.name, 1)
                repository.add_products_to_niche(products, niche.name, category.name, self.marketplace_name)

    def fill_niche_price_history(self, niche: str):
        # TODO Not implemented
        pass
