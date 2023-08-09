from abc import abstractmethod
from typing import final

from jorm.jarvis.initialization import Initializer, Initializable

from jdu.db_tools.fill.base import DBFiller


class DBFillerInitializer(Initializer):
    def __init__(self):
        super().__init__()

    def init_object(self, initializable_object: DBFiller):
        super().init_object(initializable_object)

    @final
    def _init_something(self, initializable_object: Initializable):
        initializable_object.marketplace_name = self.get_marketplace_name()

    @abstractmethod
    def get_marketplace_name(self) -> str:
        return 'default'
