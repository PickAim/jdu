"""Методы осуществляющие заполнение базы данных"""
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
from jorm.market.infrastructure import Marketplace, Category
from jorm.market.items import Product
from sqlalchemy.orm import Session

from jdu.providers.common import WildBerriesDataProviderWithoutKey


class DBFiller(ABC):
    def __init__(self):
        """Конструктор DBFiller"""
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
    """Имплементрирующий класс заполнителей БД"""

    def __init__(self, provider: WildBerriesDataProviderWithoutKey, session: Session):
        """Конструктор класса заполнителей БД"""
        super().__init__()
        self.marketplace_name: str = 'wildberries'
        self.__provider = provider
        self.__session = session
        self.__service_marketplace = MarketplaceService(MarketplaceRepository(
            self.__session),
            MarketplaceTableToJormMapper(WarehouseTableToJormMapper()))
        self.__service_category = CategoryService(CategoryRepository(session),
                                                  CategoryTableToJormMapper(NicheTableToJormMapper()))
        self.__service_niche = NicheService(NicheRepository(session), NicheTableToJormMapper())
        self.__service_product = ProductCardService(ProductCardRepository(session), ProductTableToJormMapper())
        self.__service_history_unit = ProductHistoryUnitService(ProductHistoryRepository(session))
        self.__service_price_history = ProductHistoryService(self.__service_history_unit, LeftoverService(
            LeftoverRepository(session), WarehouseRepository(session), self.__service_history_unit),
                                                             ProductHistoryRepository(session),
                                                             ProductHistoryTableToJormMapper(
                                                                 LeftoverTableToJormMapper()))

    def fill_marketplace(self):
        """Заполнить маркетплейс"""
        marketplace: Marketplace = Marketplace(self.marketplace_name)
        self.__service_marketplace.create(marketplace)

    def fill_categories(self, category_num: int = -1):
        """Заполнить категории"""
        marketplace, id_marketplace = self.__service_marketplace.find_by_name(self.marketplace_name)
        categories: list[Category] = self.__provider.get_categories(category_num)
        self.__service_category.create_all(categories, id_marketplace)

    def fill_niches(self, niche_num: int = -1):
        """Заполнить ниши"""
        marketplace, id_marketplace = self.__service_marketplace.find_by_name(self.marketplace_name)
        categories: dict[int, Category] = self.__service_category.find_all_in_marketplace(id_marketplace)
        for id_category in categories:
            niches = self.__provider.get_niches_by_category(categories[id_category].name, niche_num)
            self.__service_niche.create_all(niches, id_category)

    def fill_niche_products(self, pages_num: int = -1, count_products: int = -1):
        """Заполнить продукты"""
        marketplace, id_marketplace = self.__service_marketplace.find_by_name(self.marketplace_name)
        niches = self.__service_niche.find_all_in_marketplace(id_marketplace)
        for id_niche in niches:
            products: list[Product] = self.__provider.get_products_by_niche(niches[id_niche].name)
            self.__service_product.create_products(products, id_niche)

    def fill_niche_price_history(self, niche: str):
        """Заполнить историю цены и unit историю цены"""
        marketplace, id_marketplace = self.__service_marketplace.find_by_name(self.marketplace_name)
        niches = self.__service_niche.find_all_in_marketplace(id_marketplace)
        for id_niche in niches:
            products = self.__service_product.find_all_in_niche(id_niche)
            for id_product in products:
                self.__service_price_history.create(products[id_product].history, id_product)
                for price_history_unit in products[id_product].history.history:
                    self.__service_history_unit.create(price_history_unit, id_product)
