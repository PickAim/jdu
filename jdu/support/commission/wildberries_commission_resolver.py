import json
from typing import Any

from jorm.market.infrastructure import HandlerType
from jorm.server.providers.commision_resolver import CommissionResolver

from jdu.support.constant import (
    COMMISSION_KEY,
    RETURN_PERCENT_KEY,
    COMMISSION_WILDBERRIES_JSON,
    COMMISSION_WILDBERRIES_CSV,
)


class WildberriesCommissionResolver(CommissionResolver):
    def __init__(self):
        super().__init__()

    def get_csv_path(self) -> str:
        return COMMISSION_WILDBERRIES_CSV

    def get_json_path(self) -> str:
        return COMMISSION_WILDBERRIES_JSON

    def _get_commission_data(self, json_path: str) -> dict[str, Any]:
        with open(json_path, "r", encoding="cp1251") as json_file:
            return json.load(json_file)

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
                    },
                    RETURN_PERCENT_KEY: int(splitted[5].replace("%", "")),
                }
            json_string: str = json.dumps(commission_dict, indent=4, ensure_ascii=False)
            with open(COMMISSION_WILDBERRIES_JSON, "w", encoding="cp1251") as out_file:
                out_file.write(json_string)

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
