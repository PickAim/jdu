import os
from abc import ABC, abstractmethod

from jorm.market.infrastructure import HandlerType


class CommissionResolver(ABC):
    def __init__(self):
        self._commission_data: dict = self.__template_get_commission_data()

    @abstractmethod
    def update_commission_file(self, filepath: str) -> None:
        pass

    @abstractmethod
    def get_json_path(self) -> str:
        pass

    @abstractmethod
    def get_csv_path(self) -> str:
        pass

    @abstractmethod
    def _get_commission_data(self, json_path: str) -> dict[str, any]:
        pass

    def __template_get_commission_data(self) -> dict[str, any]:
        json_path: str = self.get_json_path()
        if not os.path.exists(json_path):
            csv_path: str = self.get_csv_path()
            self.update_commission_file(csv_path)
        return self._get_commission_data(json_path)

    @abstractmethod
    def _get_commission_for_niche(self, niche_name: str) -> dict[str, float]:
        pass

    @abstractmethod
    def get_commission_for_niche_mapped(self, niche_name: str) -> dict[HandlerType: float]:
        pass

    @abstractmethod
    def get_return_percent_for(self, niche_name: str) -> float:
        pass
