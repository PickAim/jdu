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
from jorm.market.items import ProductHistory, Product
from sqlalchemy.orm import Session

from jdu.providers.common import WildBerriesDataProviderWithoutKey


class DBFiller(ABC):
    def __init__(self):
        self.__marketplace_name: str = 'default'


class WildberriesDBFiller(DBFiller):

    @abstractmethod
    def fill_categories(self, category_num: int = -1) -> None:
        pass

    @abstractmethod
    def fill_niches(self, niche_num: int = -1) -> None:
        pass

    @abstractmethod
    def fill_products(self, products_count: int = -1) -> None:
        pass

    @abstractmethod
    def fill_price_history(self, niche: str) -> None:
        pass


class WildberriesDBFillerImpl(WildberriesDBFiller):

    def __init__(self, provider: WildBerriesDataProviderWithoutKey, session: Session):
        super().__init__()
        self.__provider = provider
        self.__marketplace_name = 'wildberries'
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
        if not self.__marketplace_service.exists_with_name(self.__marketplace_name):
            self.__marketplace_service.create(Marketplace(self.__marketplace_name))
        self.__marketplace_id = self.__marketplace_service.find_by_name(self.__marketplace_name)[1]

    def fill_categories(self, category_num: int = -1):
        categories_names: list[str] = self.__provider.get_categories_names(category_num)
        filtered_categories_names: list[str] = \
            self.__category_service.filter_existing_names(categories_names, self.__marketplace_id)
        categories: list[Category] = self.__provider.get_categories(filtered_categories_names)
        self.__category_service.create_all(categories, self.__marketplace_id)

    def fill_niches(self, niche_num: int = -1):
        categories: dict[int, Category] = self.__category_service.find_all_in_marketplace(self.__marketplace_id)
        for category_id in categories:
            niches_names: list[str] = self.__provider.get_niches_names(categories[category_id].name, niche_num)
            filtered_niches_names: list[str] = self.__niche_service.filter_existing_names(niches_names, category_id)
            niches: list[Niche] = self.__provider.get_niches(filtered_niches_names)
            self.__niche_service.create_all(niches, category_id)

    def fill_products(self, products_count: int = -1):
        niches: dict[int, Niche] = self.__niche_service.find_all_in_marketplace(self.__marketplace_id)
        for niche_id in niches:
            id_to_name_cost_dict: dict[int, tuple[str, int]] = \
                self.__provider.get_products_id_to_name_cost_dict(niches[niche_id].name, products_count)
            filtered_products_global_ids: list[int] = \
                self.__product_service.filter_existing_global_ids(id_to_name_cost_dict.keys(), niche_id)
            id_to_name_cost_list: list[tuple[int, str, int]] = [
                (global_id, id_to_name_cost_dict[global_id][0], id_to_name_cost_dict[global_id][1])
                for global_id in filtered_products_global_ids
            ]
            products: list[Product] = \
                self.__provider.get_products(niches[niche_id].name, id_to_name_cost_list)
            self.__product_service.create_products(products, niche_id)

    def fill_price_history(self, niche: str):
        niches: dict[int, Niche] = self.__niche_service.find_all_in_marketplace(self.__marketplace_id)
        for niche_id in niches:
            products: dict[int, Product] = self.__product_service.find_all_in_niche(niche_id)
            for product_id in products:
                price_history: ProductHistory = self.__provider.get_product_price_history(product_id)
                self.__price_history_service.create(price_history, product_id)
