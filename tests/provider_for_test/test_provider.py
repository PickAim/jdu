from datetime import datetime

from jorm.market.infrastructure import Niche, Product, HandlerType, Category
from jorm.market.items import ProductHistoryUnit, ProductHistory
from jorm.support.types import StorageDict, SpecifiedLeftover

from jdu.providers.common import WildBerriesDataProviderWithoutKey


class WildBerriesDataProviderWithoutKeyImplTest(WildBerriesDataProviderWithoutKey):

    def __init__(self):
        super().__init__()

    def get_categories_names(self, category_num=-1) -> list[str]:
        category_names_list: list[str] = []
        for i in range(category_num):
            category_names_list.append('Category_' + i.__str__())
        return category_names_list

    def get_categories(self, category_names_list) -> list[Category]:
        category_list: list[Category] = []
        for category_name in category_names_list:
            category_list.append(Category(category_name))
        return category_list

    def get_niches_names(self, category, niche_num=-1) -> list[str]:
        niche_names_list: list[str] = []
        for i in range(niche_num):
            niche_names_list.append('Niche_' + i.__str__())
        return niche_names_list

    def get_niches(self, niche_names_list) -> list[Niche]:
        niche_list = []
        for niche_name in niche_names_list:
            niche_list.append(Niche(niche_name, {
                HandlerType.MARKETPLACE: 0,
                HandlerType.PARTIAL_CLIENT: 0,
                HandlerType.CLIENT: 0}, 0))
        return niche_list

    def get_products_id_to_name_cost_dict(self, niche: str, pages_num: int,
                                          products_count: int) -> dict[int, tuple[str, int]]:
        id_to_name_cost_dict: dict[int, tuple[str, int]] = {}
        for i in range(10):
            id_to_name_cost_dict[i] = ('Product_' + i.__str__(), i)
        return id_to_name_cost_dict

    async def load_all_product_niche(self) -> list[Product]:
        pass

    def get_products(self, niche: str, products_global_ids: list[int], filtered_products_global_ids: list[int],
                     pages_num: int = -1, count_products: int = -1) -> \
            list[Product]:
        products_list: list[Product] = []
        for i in filtered_products_global_ids:
            products_list.append(Product('Product_' + i.__str__(), i, i, i, ProductHistory()))
        return products_list

    def get_price_history(self, product_id: int) -> ProductHistory:
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
