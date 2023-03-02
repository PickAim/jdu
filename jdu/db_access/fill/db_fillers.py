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
    def fill_categories(self, category_num: int = -1, niche_num: int = -1, product_num: int = -1) -> None:
        pass

    @abstractmethod
    def fill_niches(self, niche_num: int = -1, product_num: int = -1) -> None:
        pass

    @abstractmethod
    def fill_niche_products(self, product_num: int = -1) -> None:
        pass

    @abstractmethod
    def fill_niche_price_history(self, niche: str) -> None:
        pass


class WildberriesDBFillerImpl(WildberriesDbFiller):

    def __init__(self, provider: WildBerriesDataProviderWithoutKey, session: Session):
        super().__init__()
        self.marketplace_name: str = 'wildberries'
        self.__provider = provider
        self.__session = session
        self.__category_repository: CategoryRepository = CategoryRepository(
            self.__session, CategoryTableToJormMapper(NicheTableToJormMapper()),
            CategoryJormToTableMapper(NicheJormToTableMapper()))
        self.__niche_repository: NicheRepository = NicheRepository(
            self.__session, NicheTableToJormMapper(), NicheJormToTableMapper())
        self.__product_repository: ProductCardRepository = ProductCardRepository(
            self.__session, ProductTableToJormMapper(), ProductJormToTableMapper())

    def fill_categories(self, category_num: int = -1, niche_num: int = -1, product_num: int = -1):
        categories: list[Category] = self.__provider.get_categories(category_num, niche_num, product_num)
        self.__category_repository.add_all_categories_to_marketplace(categories, self.marketplace_name)

    def fill_niches(self, niche_num: int = -1, product_num: int = -1):
        categories: list[Category] = self.__category_repository.fetch_marketplace_categories(self.marketplace_name)
        for category in categories:
            niches = self.__provider.get_niches_by_category(category.name, niche_num, product_num)
            self.__niche_repository.add_all_by_category_name(niches, category.name, self.marketplace_name)

    def fill_niche_products(self, product_num: int = -1):
        categories: list[Category] = self.__category_repository.fetch_marketplace_categories(self.marketplace_name)
        for category in categories:
            niches: list[Niche] = self.__niche_repository.fetch_niches_by_category(category.name, self.marketplace_name)
            for niche in niches:
                products: list[Product] = self.__provider.get_products_by_niche(niche.name)
                self.__product_repository.add_products_to_niche(products, niche.name, category.name,
                                                                self.marketplace_name)

    def fill_niche_price_history(self, niche: str):
        # TODO Not implemented
        pass
