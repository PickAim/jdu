from datetime import datetime

from jorm.market.infrastructure import Niche, Product, HandlerType, Category, Warehouse, Address
from jorm.market.items import ProductHistoryUnit, ProductHistory
from jorm.support.types import StorageDict, SpecifiedLeftover

from jdu.providers.common import WildBerriesDataProviderWithoutKey, WildBerriesDataProviderWithKey


class WildBerriesDataProviderWithoutKeyImplTest(WildBerriesDataProviderWithoutKey):

    def __init__(self):
        super().__init__()

    def __del__(self):
        self._session.close()

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

    def get_products_id_to_name_cost_dict(self, niche: str,
                                          pages_num: int = -1,
                                          products_count: int = -1) -> dict[int, tuple[str, int]]:
        id_to_name_cost_dict: dict[int, tuple[str, int]] = {}
        for i in range(10):
            id_to_name_cost_dict[i] = ('Product_' + i.__str__(), i)
        return id_to_name_cost_dict

    async def load_all_product_niche(self) -> list[Product]:
        pass

    def get_products(self, niche: str, category: str, id_to_name_cost_dict: list[tuple[int, str, int]]) -> list[
        Product]:
        products_list: list[Product] = []
        for i in id_to_name_cost_dict:
            products_list.append(
                Product('Product_' + i[0].__str__(), i[0], i[0], i[0], "brand", "seller", "Niche_" + i[0].__str__(),
                        "Category_" + i[0].__str__(), ProductHistory())
            )
        return products_list

    def get_product_price_history(self, product_id: int) -> ProductHistory:
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


class WildBerriesDataProviderStandardImplTest(WildBerriesDataProviderWithKey):
    def __init__(self):
        super().__init__("api-key")

    def __del__(self):
        self._session.close()

    def get_warehouses(self) -> list[Warehouse]:
        warehouses: list[Warehouse] = []
        for i in range(10):
            warehouses.append(
                Warehouse('warehouse_' + i.__str__(), i, HandlerType.MARKETPLACE, Address('Address_' + i.__str__())))
        return warehouses
