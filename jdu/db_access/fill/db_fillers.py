from abc import ABC
from abc import abstractmethod

from jarvis_db.repositores.mappers.market.infrastructure import CategoryTableToJormMapper, NicheTableToJormMapper, \
    NicheJormToTableMapper, CategoryJormToTableMapper, MarketplaceTableToJormMapper, WarehouseTableToJormMapper
from jarvis_db.repositores.market.infrastructure import CategoryRepository, NicheRepository, MarketplaceRepository
from jarvis_db.repositores.market.items import ProductCardRepository, ProductHistoryRepository
from jarvis_db.services.market.infrastructure.marketplace_service import MarketplaceService
from jarvis_db.tables import Marketplace
from jorm.market.infrastructure import Marketplace
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
            self.__session)
        self.__marketplace_repository: MarketplaceRepository = MarketplaceRepository(
            self.__session)
        self.__service_marketplace = MarketplaceService(self.__marketplace_repository,
                                                        MarketplaceTableToJormMapper(WarehouseTableToJormMapper()))
        self.__history_repository = ProductHistoryRepository(
            self.__session)

    def fill_marketplace(self):
        marketplace: Marketplace = Marketplace(self.marketplace_name)
        self.__service_marketplace.create(marketplace)

    def fill_categories(self, category_num: int = -1):
        # marketplace: Marketplace = self.__marketplace_repository.find_by_name(self.marketplace_name)
        # categories: list[Category] = self.__provider.get_categories(category_num)
        # self.__category_repository.add_all(categories, marketplace.id)
        pass

    def fill_niches(self, niche_num: int = -1):
        # marketplace = self.__marketplace_repository.find_by_name(self.marketplace_name)
        # categories: dict[int: Category] = self.__category_repository.find_all(marketplace.id)
        # for id_category in categories:
        #     niches = self.__provider.get_niches_by_category(categories[id_category].name, niche_num)
        #     self.__niche_repository.add_all(niches, id_category)
        pass

    def fill_niche_products(self, pages_num: int = -1, count_products: int = -1):
        # marketplace = self.__marketplace_repository.find_by_name(self.marketplace_name)
        # categories: dict[int: Category] = self.__category_repository.find_all(marketplace.id)
        # for id_category in categories:
        #     niches: dict[int: Niche] = self.__niche_repository.fetch_niches_by_category(id_category)
        #     for id_niche in niches:
        #         products: list[Product] = self.__provider.get_products_by_niche(niches[id_niche].name, pages_num,
        #                                                                         count_products)
        #         self.__product_repository.add(products)
        pass

    def fill_niche_price_history(self, niche: str):
        # dict_marketplaces = self.__marketplace_repository.fetch_all()
        # categories: dict[int: Category] = {}
        # for id_marketplace in dict_marketplaces:
        #     categories = self.__category_repository.find_all(id_marketplace)
        # for id_category in categories:
        #     niches: dict[int: Niche] = self.__niche_repository.fetch_niches_by_category(id_category)
        #     for id_niche in niches:
        #         products: dict[int, Product] = self.__product_repository.fetch_all_in_niche(id_niche)
        #         for id_product in products:
        #             self.__history_repository.add(products[id_product].history.history,
        #                                           id_product)
        pass
