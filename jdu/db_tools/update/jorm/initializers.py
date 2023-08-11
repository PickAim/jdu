from abc import ABC, abstractmethod

from jorm.jarvis.initialization import Initializer
from sqlalchemy.orm import Session

from jdu.db_tools.update.jorm.base import JORMChangerBase


class JORMChangerInitializer(Initializer, ABC):
    def __init__(self, session: Session):
        super().__init__()
        self.session = session

    def init_object(self, initializable_object: JORMChangerBase):
        super().init_object(initializable_object)

    @abstractmethod
    def _init_something(self, jorm_changer: JORMChangerBase):
        pass
