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
from jarvis_db.services.market.infrastructure.warehouse_service import WarehouseService
from jarvis_db.services.market.items.leftover_service import LeftoverService
from jarvis_db.services.market.items.product_card_service import ProductCardService
from jarvis_db.services.market.items.product_history_service import ProductHistoryService
from jarvis_db.services.market.items.product_history_unit_service import ProductHistoryUnitService
from jarvis_db.tables import Marketplace, Warehouse
from jorm.market.infrastructure import Marketplace, Category, Niche
from jorm.market.items import ProductHistory, Product
from sqlalchemy.orm import Session

from jdu.providers import WildBerriesDataProviderStandardImpl
from jdu.providers.common import WildBerriesDataProviderWithoutKey


class DBFiller(ABC):
    def __init__(self):
        self.marketplace_name: str = 'default'


class WildberriesDBFiller(DBFiller):
    def __init__(self, session: Session):
        super().__init__()
        self.marketplace_name = 'wildberries'
        self.marketplace_service = MarketplaceService(MarketplaceRepository(
            session),
            MarketplaceTableToJormMapper(WarehouseTableToJormMapper()))
        self.category_service = CategoryService(CategoryRepository(session),
                                                CategoryTableToJormMapper(NicheTableToJormMapper()))
        self.niche_service = NicheService(NicheRepository(session), NicheTableToJormMapper())
        self.product_service = ProductCardService(ProductCardRepository(session), ProductTableToJormMapper())
        self.history_unit_service = ProductHistoryUnitService(ProductHistoryRepository(session))
        self.warehouse_service = WarehouseService(WarehouseRepository(session), WarehouseTableToJormMapper())
        self.price_history_service = ProductHistoryService(self.history_unit_service, LeftoverService(
            LeftoverRepository(session), WarehouseRepository(session), self.history_unit_service),
                                                           ProductHistoryRepository(session),
                                                           ProductHistoryTableToJormMapper(
                                                               LeftoverTableToJormMapper()))
        if not self.marketplace_service.exists_with_name(self.marketplace_name):
            self.marketplace_service.create(Marketplace(self.marketplace_name))
        self.marketplace_id = self.marketplace_service.find_by_name(self.marketplace_name)[1]


class WildberriesDBFillerWithKey(WildberriesDBFiller):
    def __init__(self, provider_with_key: WildBerriesDataProviderStandardImpl, session: Session):
        super().__init__(session)
        self.provider_with_key = provider_with_key

    @abstractmethod
    def fill_warehouse(self) -> None:
        pass


class WildberriesDBFillerWithoutKey(WildberriesDBFiller):
    def __init__(self, provider_without_key: WildBerriesDataProviderWithoutKey, session: Session):
        super().__init__(session)
        self.provider_without_key = provider_without_key

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


class WildberriesDBFillerWithoutKeyImpl(WildberriesDBFillerWithoutKey):

    def __init__(self, provider_without_key: WildBerriesDataProviderWithoutKey, session: Session):
        super().__init__(provider_without_key, session)

    def fill_categories(self, category_num: int = -1):
        categories_names: list[str] = self.provider_without_key.get_categories_names(category_num)
        filtered_categories_names: list[str] = \
            self.category_service.filter_existing_names(categories_names, self.marketplace_id)
        categories: list[Category] = self.provider_without_key.get_categories(filtered_categories_names)
        self.category_service.create_all(categories, self.marketplace_id)

    def fill_niches(self, niche_num: int = -1):
        categories: dict[int, Category] = self.category_service.find_all_in_marketplace(self.marketplace_id)
        for category_id in categories:
            niches_names: list[str] = self.provider_without_key.get_niches_names(categories[category_id].name,
                                                                                 niche_num)
            filtered_niches_names: list[str] = self.niche_service.filter_existing_names(niches_names, category_id)
            niches: list[Niche] = self.provider_without_key.get_niches(filtered_niches_names)
            self.niche_service.create_all(niches, category_id)

    def fill_products(self, products_count: int = -1):
        categories: dict[int, Category] = self.category_service.find_all_in_marketplace(self.marketplace_id)
        for category_id in categories:
            niche_dict = self.niche_service.find_all_in_category(category_id)
            for niche_id in niche_dict:
                id_to_name_cost_dict: dict[int, tuple[str, int]] = \
                    self.provider_without_key.get_products_id_to_name_cost_dict(niche_dict[niche_id].name,
                                                                                products_count)
                filtered_products_global_ids: list[int] = \
                    self.product_service.filter_existing_global_ids(id_to_name_cost_dict.keys())
                id_to_name_cost_list: list[tuple[int, str, int]] = [
                    (global_id, id_to_name_cost_dict[global_id][0], id_to_name_cost_dict[global_id][1])
                    for global_id in filtered_products_global_ids
                ]
                products: list[Product] = \
                    self.provider_without_key.get_products(niche_dict[niche_id].name, categories[category_id].name,
                                                           id_to_name_cost_list)
                self.product_service.create_products(products, niche_id)

    def fill_price_history(self, niche: str):
        niches: dict[int, Niche] = self.niche_service.find_all_in_marketplace(self.marketplace_id)
        for niche_id in niches:
            products: dict[int, Product] = self.product_service.find_all_in_niche(niche_id)
            for product_id in products:
                price_history: ProductHistory = self.provider_without_key.get_product_price_history(product_id)
                self.price_history_service.create(price_history, product_id)


class WildberriesDBFillerWithKeyImpl(WildberriesDBFillerWithKey):
    def __init__(self, provider_with_key: WildBerriesDataProviderStandardImpl, session: Session):
        super().__init__(provider_with_key, session)

    def fill_warehouse(self):
        warehouses: list[Warehouse] = self.provider_with_key.get_warehouses()
        self.warehouse_service.create_all(warehouses, self.marketplace_id)
