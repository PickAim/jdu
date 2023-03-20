from abc import ABC
from abc import abstractmethod

from jarvis_db.repositores.mappers.market.infrastructure import CategoryTableToJormMapper, NicheTableToJormMapper, \
    NicheJormToTableMapper, CategoryJormToTableMapper, MarketplaceTableToJormMapper, WarehouseTableToJormMapper, \
    MarketplaceJormToTableMapper, WarehouseJormToTableMapper
from jarvis_db.repositores.mappers.market.items import ProductTableToJormMapper, ProductJormToTableMapper
from jarvis_db.repositores.market.infrastructure import CategoryRepository, NicheRepository, MarketplaceRepository
from jarvis_db.repositores.market.items import ProductCardRepository
from jorm.market.infrastructure import Category, Niche, Marketplace
from jorm.market.items import Product
from sqlalchemy.orm import Session

from jdu.providers.common import WildBerriesDataProviderWithoutKey


class DBFiller(ABC):
    def __init__(self):
        self.marketplace_name: str = 'default'


class WildberriesDbFiller(DBFiller):
    @abstractmethod
    def fill_marketplace(self) -> None:
        pass

    @abstractmethod
    def fill_categories(self, category_num: int = -1) -> None:
        pass

    @abstractmethod
    def fill_niches(self, niche_num: int = -1) -> None:
        pass

    @abstractmethod
    def fill_niche_products(self, pages_num: int = -1, count_products: int = -1) -> None:
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
        self.__marketplace_repository: MarketplaceRepository = MarketplaceRepository(
            self.__session, MarketplaceTableToJormMapper(
                WarehouseTableToJormMapper()),
            MarketplaceJormToTableMapper(WarehouseJormToTableMapper()))

    def fill_marketplace(self):
        marketplace: Marketplace = Marketplace(self.marketplace_name)
        self.__marketplace_repository.add(marketplace)

    def fill_categories(self, category_num: int = -1):
        dict_marketplaces = self.__marketplace_repository.fetch_all()
        categories: list[Category] = self.__provider.get_categories(category_num)
        for id_marketplace in dict_marketplaces:
            self.__category_repository.add_all_categories_to_marketplace(categories, id_marketplace)

    def fill_niches(self, niche_num: int = -1):
        dict_marketplaces = self.__marketplace_repository.fetch_all()
        categories: dict[int: Category] = {}
        for id_marketplace in dict_marketplaces:
            categories = self.__category_repository.fetch_marketplace_categories(id_marketplace)
        for id_category in categories:
            niches = self.__provider.get_niches_by_category(categories[id_category].name, niche_num)
            self.__niche_repository.add_all(niches, id_category)

    def fill_niche_products(self, pages_num: int = -1, count_products: int = -1):
        dict_marketplaces = self.__marketplace_repository.fetch_all()
        categories: dict[int: Category] = {}
        for id_marketplace in dict_marketplaces:
            categories = self.__category_repository.fetch_marketplace_categories(id_marketplace)
        for id_category in categories:
            niches: dict[int: Niche] = self.__niche_repository.fetch_niches_by_category(id_category)
            for id_niche in niches:
                products: list[Product] = self.__provider.get_products_by_niche(niches[id_niche].name, pages_num,
                                                                                count_products)
                self.__product_repository.add_products_to_niche(products, id_niche)

    def fill_niche_price_history(self, niche: str):
        # TODO Not implemented
        pass
