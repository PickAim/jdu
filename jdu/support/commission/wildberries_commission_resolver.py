from jorm.market.infrastructure import HandlerType
from jorm.server.providers.commision_resolver import CommissionResolver
from jser.niche.commission.serialize_niche_commission import get_commission_data
from jser.warehouse.commision.serialize_warehouse_commision import get_warehouse_data

from jdu.support.constant import (
    RETURN_PERCENT_KEY,
)


class WildberriesCommissionResolver(CommissionResolver):

    def __init__(self):
        super().__init__()

    def _get_commission_for_niche(self, niche_name: str) -> dict[str, float]:
        # TODO Yeah, i didn't want to make jorm dependent on jser
        self._commission_data = get_commission_data()
        if niche_name not in self._commission_data:
            return {
                HandlerType.MARKETPLACE.value: 0,
                HandlerType.PARTIAL_CLIENT.value: 0,
                HandlerType.CLIENT.value: 0,
            }
        return self._commission_data[niche_name]["commission"]

    def get_commission_for_niche_mapped(self, niche_name: str) -> dict:
        commission_for_niche: dict = self._get_commission_for_niche(niche_name)
        return {
            HandlerType.MARKETPLACE: commission_for_niche[
                HandlerType.MARKETPLACE.value
            ],
            HandlerType.PARTIAL_CLIENT: commission_for_niche[
                HandlerType.PARTIAL_CLIENT.value
            ],
            HandlerType.CLIENT: commission_for_niche[HandlerType.CLIENT.value],
        }

    def get_return_percent_for(self, niche_name: str) -> float:
        if niche_name not in self._commission_data:
            return 0.0
        return self._commission_data[niche_name][RETURN_PERCENT_KEY] / 100

    def mapping_warehouse_data(self):
        # TODO Yeah, i didn't want to make jorm dependent on jser
        self._warehouse_data = get_warehouse_data()
        warehouses_data = self._warehouse_data['result']['resp']['data']
        warehouse_dict: dict[int, any] = {}
        for data in warehouses_data:
            template_dict = {}
            template_dict['name'] = data['warehouse']
            template_dict['address'] = data['address']
            template_dict['isFbs'] = data['isFbs']
            template_dict['isFbw'] = data['isFbw']
            template_dict['rating'] = data['rating']
            if "scanPrices" not in data:
                template_dict['scanPrices'] = []
            else:
                template_dict['scanPrices'] = data['scanPrices']
            warehouse_dict[data['id']] = template_dict
        return warehouse_dict

    def get_data_for_warehouse(self, id: int):
        mapping_warehouse = self.mapping_warehouse_data()
        return {id: mapping_warehouse[id]}
