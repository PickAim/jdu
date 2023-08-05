from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from jdu.db_tools.update.jorm.base import JORMChangerBase


class JORMChangerInitializer(ABC):
    @staticmethod
    @abstractmethod
    def init_jorm_changer(session: Session, jorm_changer: JORMChangerBase):
        pass
