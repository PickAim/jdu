from jorm.market.infrastructure import HandlerType
from jser.JserResolver.commission_resolver import JserCommissionResolver

from jdu.support.constant import (
    RETURN_PERCENT_KEY,
)


class WildberriesCommissionResolver(JserCommissionResolver):

    def __init__(self):
        super().__init__()

    def _get_commission_for_niche(self, niche_name: str) -> dict[str, float]:
        if niche_name not in self._niche_commission_data:
            return {
                HandlerType.MARKETPLACE.value: 0,
                HandlerType.PARTIAL_CLIENT.value: 0,
                HandlerType.CLIENT.value: 0,
            }
        return self._niche_commission_data[niche_name]["commission"]

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
        if niche_name not in self._niche_commission_data:
            return 0.0
        return self._niche_commission_data[niche_name][RETURN_PERCENT_KEY] / 100
