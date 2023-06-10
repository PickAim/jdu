from jorm.jarvis.db_update import JORMChanger
from jorm.market.infrastructure import Niche
from jorm.market.service import (
    FrequencyRequest,
    FrequencyResult,
    RequestInfo,
    UnitEconomyRequest,
    UnitEconomyResult,
)

from jarvis_db.services.market.service.economy_service import EconomyService
from jarvis_db.services.market.service.frequency_service import FrequencyService


class JormChangerImpl(JORMChanger):
    def __init__(
        self, economy_service: EconomyService, frequency_service: FrequencyService
    ):
        self.__economy_service = economy_service
        self.__frequency_service = frequency_service

    def save_unit_economy_request(
        self,
        request: UnitEconomyRequest,
        result: UnitEconomyResult,
        request_info: RequestInfo,
        user_id: int,
    ) -> int:
        self.__economy_service.save_request(request_info, request, result, user_id, 0)
        return 0

    def save_frequency_request(
        self,
        request: FrequencyRequest,
        result: FrequencyResult,
        request_info: RequestInfo,
        user_id: int,
    ) -> int:
        self.__frequency_service.save(request_info, request, result, user_id)
        return 0

    def delete_unit_economy_request(self, request_id: int, user_id: int) -> None:
        self.__economy_service.remove(request_id)

    def delete_frequency_request(self, request_id: int, user_id: int) -> None:
        self.__economy_service.remove(request_id)

    def load_new_niche(self, niche_name: str) -> Niche:
        return super().load_new_niche(niche_name)
