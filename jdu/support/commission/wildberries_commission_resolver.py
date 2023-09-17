import ast
import json
import pickle
from typing import Any

from jorm.market.infrastructure import HandlerType
from jorm.server.providers.commision_resolver import CommissionResolver

from jdu.support.constant import (
    COMMISSION_KEY,
    RETURN_PERCENT_KEY,
    COMMISSION_WILDBERRIES_BINARY,
    COMMISSION_WILDBERRIES_CSV, WAREHOUSE_WILDBERRIES_JSON, WAREHOUSE_WILDBERRIES_BINARY, )


class WildberriesCommissionResolver(CommissionResolver):

    def __init__(self):
        super().__init__()

    def get_commision_csv_path(self) -> str:
        return COMMISSION_WILDBERRIES_CSV

    def get_commision_binary_path(self) -> str:
        return COMMISSION_WILDBERRIES_BINARY

    def get_warehouse_file_path(self) -> str:
        return WAREHOUSE_WILDBERRIES_JSON

    def get_warehouse_binary_path(self) -> str:
        return WAREHOUSE_WILDBERRIES_BINARY

    def _get_commission_data(self, binary_path: str) -> dict[str, Any]:
        with open(binary_path, 'rb') as f:
            return ast.literal_eval(pickle.load(f))

    def update_commission_file(self, filepath: str) -> None:
        with open(filepath, "r", encoding="cp1251") as file:
            commission_dict: dict = {}
            lines: list[str] = file.readlines()
            for line in lines:
                splitted: list[str] = line.split(";")
                commission_dict[splitted[1].lower()] = {
                    COMMISSION_KEY: {
                        HandlerType.MARKETPLACE.value: float(splitted[2]) / 100,
                        HandlerType.PARTIAL_CLIENT.value: float(splitted[3]) / 100,
                        HandlerType.CLIENT.value: float(splitted[4]) / 100,
                    }
                }
            json_string: str = json.dumps(commission_dict, indent=4, ensure_ascii=False)
            with open(COMMISSION_WILDBERRIES_BINARY, 'wb') as out_file:
                pickle.dump(json_string, out_file)

    def _get_commission_for_niche(self, niche_name: str) -> dict[str, float]:
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

    def update_warehouse_file(self, filepath: str):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        with open('warehouse_data.pickle', 'wb') as f:
            pickle.dump(data, f)

    def _get_warehouse_data(self, binary_path: str):
        with open(binary_path, 'rb') as f:
            return pickle.load(f)

    def serealize_warehouse_data(self):
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

    def get_commision_for_warehouse(self, id: str):
        return self.serealize_warehouse_data()
