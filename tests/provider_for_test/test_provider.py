from datetime import datetime

from aiohttp import ClientSession
from jorm.market.infrastructure import Niche, Product, HandlerType, Category
from jorm.market.items import ProductHistoryUnit, ProductHistory
from jorm.support.types import StorageDict, SpecifiedLeftover

from jdu.providers.common import WildBerriesDataProviderWithoutKey


class WildBerriesDataProviderWithoutKeyImplTest(WildBerriesDataProviderWithoutKey):

    def __init__(self):
        super().__init__()

    def get_categories(self, category_num=-1) -> list[Category]:
        categories_list: list[Category] = []
        categories_to_add = 10
        for i in range(categories_to_add):
            categories_list.append(Category('Category_' + i.__str__()))
        return categories_list

    def get_niches_by_category(self, name_category: str, niche_num: int = -1) -> list[Niche]:
        niches_to_add = 10
        niche_list = []
        for i in range(niches_to_add):
            niche_list.append(Niche('Niche_' + i.__str__(), {
                HandlerType.MARKETPLACE: 0,
                HandlerType.PARTIAL_CLIENT: 0,
                HandlerType.CLIENT: 0}, 0))
        return niche_list

    async def load_all_product_niche(self) -> list[Product]:
        pass

    def get_products_by_niche(self, niche: str, pages_num: int = -1, count_products: int = -1) -> list[Product]:
        products_list: list[Product] = []
        for i in range(10):
            products_list.append(Product('Product_' + i.__str__(), i, i, i, ProductHistory()))
        return products_list

    async def get_product_price_history(self, session: ClientSession, product_id: int) -> ProductHistory:
        units = [ProductHistoryUnit(
            i * 10, datetime.utcnow(), StorageDict()) for i in range(1, 11)]
        return ProductHistory(units)

    def get_storage_dict(self, product_id: int) -> StorageDict:
        storage_dict: StorageDict = StorageDict()
        specified_leftover_list: list[SpecifiedLeftover] = []
        for i in range(10):
            specified_leftover_list.append(SpecifiedLeftover('SpecifyName_' + i.__str__(), i))
            storage_dict[i] = specified_leftover_list
        return storage_dict
