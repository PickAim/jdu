from abc import ABC, abstractmethod

from jorm.market.infrastructure import Category, Niche, Product
from jorm.market.items import ProductHistory


class Provider(ABC):
    pass


class WildBerriesDataProvider(Provider):
    @abstractmethod
    def __init__(self, api_key: str):
        pass

    @staticmethod
    @abstractmethod
    def get_categories() -> list[Category]:
        pass

    @abstractmethod
    def get_niches_by_category(self, category: str) -> list[Niche]:
        # TODO implement request.request_utils.get_object_names for it now
        pass

    @abstractmethod
    def get_products_by_niche(self, niche: str) -> list[Product]:
        pass

    @abstractmethod
    def get_product_price_history(self, product_id: int) -> ProductHistory:
        # TODO look at request.request_utils.get_page_data
        pass
