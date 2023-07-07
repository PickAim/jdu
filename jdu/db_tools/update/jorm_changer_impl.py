from jarvis_db.services.market.service.economy_service import EconomyService
from jarvis_db.services.market.service.frequency_service import FrequencyService
from jorm.jarvis.db_update import JORMChanger
from jorm.market.infrastructure import Niche
from jorm.market.service import (
    FrequencyRequest,
    FrequencyResult,
    RequestInfo,
    UnitEconomyRequest,
    UnitEconomyResult,
)

from jdu.db_tools.fill.db_fillers import StandardDBFiller


class JormChangerImpl(JORMChanger):

    def __init__(
            self, economy_service: EconomyService, frequency_service: FrequencyService, db_filler: StandardDBFiller
    ):
        self.__economy_service = economy_service
        self.__frequency_service = frequency_service
        self.__db_filler = db_filler

    def save_unit_economy_request(self, request: UnitEconomyRequest, result: UnitEconomyResult,
                                  request_info: RequestInfo, user_id: int) -> int:
        return self.__economy_service.save_request(request_info, request, result, user_id, request.marketplace_id)

    def save_frequency_request(
            self,
            request: FrequencyRequest,
            result: FrequencyResult,
            request_info: RequestInfo,
            user_id: int,
    ) -> int:
        return self.__frequency_service.save(request_info, request, result, user_id)

    def delete_unit_economy_request(self, request_id: int, user_id: int) -> None:
        self.__economy_service.remove(request_id)

    def delete_frequency_request(self, request_id: int, user_id: int) -> None:
        self.__economy_service.remove(request_id)

    def load_new_niche(self, niche_name: str) -> Niche:
        return self.__db_filler.fill_niche_by_name(niche_name)
