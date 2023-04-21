from abc import ABC
from abc import abstractmethod

from jarvis_db.repositores.mappers.market.infrastructure import NicheTableToJormMapper, \
    MarketplaceTableToJormMapper, WarehouseTableToJormMapper, CategoryTableToJormMapper
from jarvis_db.repositores.mappers.market.items import ProductTableToJormMapper, ProductHistoryTableToJormMapper
from jarvis_db.repositores.mappers.market.items.leftover_mappers import LeftoverTableToJormMapper
from jarvis_db.repositores.market.infrastructure import CategoryRepository, NicheRepository, MarketplaceRepository, \
    WarehouseRepository
from jarvis_db.repositores.market.items import ProductCardRepository, ProductHistoryRepository
from jarvis_db.repositores.market.items.leftover_repository import LeftoverRepository
from jarvis_db.services.market.infrastructure.category_service import CategoryService
from jarvis_db.services.market.infrastructure.marketplace_service import MarketplaceService
from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.services.market.items.leftover_service import LeftoverService
from jarvis_db.services.market.items.product_card_service import ProductCardService
from jarvis_db.services.market.items.product_history_service import ProductHistoryService
from jarvis_db.services.market.items.product_history_unit_service import ProductHistoryUnitService
from jarvis_db.tables import Marketplace
from jorm.market.infrastructure import Marketplace, Category, Niche
from jorm.market.items import Product
from sqlalchemy.orm import Session

from jdu.providers.common import WildBerriesDataProviderWithoutKey


class DBFiller(ABC):
    def __init__(self):
        self.marketplace_name: str = 'default'


class WildberriesDBFiller(DBFiller):

    @abstractmethod
    def fill_categories(self, category_num: int = -1) -> None:
        pass

    @abstractmethod
    def fill_niches(self, niche_num: int = -1) -> None:
        pass

    @abstractmethod
    def fill_products(self, pages_num: int = -1, products_count: int = -1) -> None:
        pass

    @abstractmethod
    def fill_price_history(self, niche: str) -> None:
        pass


class WildberriesDBFillerImpl(WildberriesDBFiller):

    def __init__(self, provider: WildBerriesDataProviderWithoutKey, session: Session):
        super().__init__()
        self.marketplace_name: str = 'wildberries'
        self.__provider = provider
        self.__marketplace_service = MarketplaceService(MarketplaceRepository(
            session),
            MarketplaceTableToJormMapper(WarehouseTableToJormMapper()))
        self.__category_service = CategoryService(CategoryRepository(session),
                                                  CategoryTableToJormMapper(NicheTableToJormMapper()))
        self.__niche_service = NicheService(NicheRepository(session), NicheTableToJormMapper())
        self.__product_service = ProductCardService(ProductCardRepository(session), ProductTableToJormMapper())
        self.__history_unit_service = ProductHistoryUnitService(ProductHistoryRepository(session))
        self.__price_history_service = ProductHistoryService(self.__history_unit_service, LeftoverService(
            LeftoverRepository(session), WarehouseRepository(session), self.__history_unit_service),
                                                             ProductHistoryRepository(session),
                                                             ProductHistoryTableToJormMapper(
                                                                 LeftoverTableToJormMapper()))
        if not self.__marketplace_service.exists_with_name(self.marketplace_name):
            self.__marketplace_service.create(Marketplace(self.marketplace_name))
        self.__marketplace_id = self.__marketplace_service.find_by_name(self.marketplace_name)[1]

    def fill_categories(self, category_num: int = -1):
        categories_name: list[str] = self.__provider.get_categories_names(category_num)
        filtered_categories_name: list[str] = \
            self.__category_service.filter_existing_names(categories_name, self.__marketplace_id)
        categories: list[Category] = self.__provider.get_categories(filtered_categories_name)
        self.__category_service.create_all(categories, self.__marketplace_id)

    def fill_niches(self, niche_num: int = -1):
        categories: dict[int, Category] = self.__category_service.find_all_in_marketplace(self.__marketplace_id)
        for category_id in categories:
            niches_name: list[str] = self.__provider.get_niches_names(categories[category_id].name, niche_num)
            filtered_niches_name: list[str] = self.__niche_service.filter_existing_names(niches_name, category_id)
            niches: list[Niche] = self.__provider.get_niches(filtered_niches_name)
            self.__niche_service.create_all(niches, category_id)

    def fill_products(self, pages_num: int = -1, products_count: int = -1):

        niches = self.__niche_service.find_all_in_marketplace(self.__marketplace_id)
        for niche_id in niches:
            products: list[Product] = self.__provider.get_products(niches[niche_id].name, pages_num,
                                                                   products_count)
            self.__product_service.create_products(products, niche_id)

    def fill_price_history(self, niche: str):
        # marketplace, id_marketplace = self.__service_marketplace.find_by_name(self.marketplace_name)
        # niches = self.__service_niche.find_all_in_marketplace(id_marketplace)
        # for id_niche in niches:
        #     products = self.__service_product.find_all_in_niche(id_niche)
        #     for id_product in products:
        #         self.__service_price_history.create(products[id_product].history, id_product)
        #         for price_history_unit in products[id_product].history.history:
        #             self.__service_history_unit.create(price_history_unit, id_product)
        pass
