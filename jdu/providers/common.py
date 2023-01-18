from abc import ABC, abstractmethod
from datetime import datetime


class Provider(ABC):
    pass


class WildBerriesDataProvider(Provider):

    @staticmethod
    @abstractmethod
    def get_categories() -> list[str]:
        pass

    @abstractmethod
    def get_niches(self, categories) -> dict[str, list[str]]:
        # TODO use get_niches_by_category for it now
        pass

    @abstractmethod
    def get_niches_by_category(self, category: str) -> list[str]:
        # TODO implement request.request_utils.get_object_names for it now
        pass

    @abstractmethod
    def get_products_by_niche(self, niche: str, pages: int) -> list[tuple[str, int]]:
        pass

    @abstractmethod
    def get_product_price_history(self, product_id: int) -> list[tuple[int, datetime]]:
        # TODO look at request.request_utils.get_page_data
        pass
