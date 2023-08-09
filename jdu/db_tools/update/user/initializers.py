from abc import ABC, abstractmethod

from jorm.jarvis.initialization import Initializer
from sqlalchemy.orm import Session

from jdu.db_tools.update.user.base import UserInfoChangerBase


class UserInfoChangerInitializer(Initializer, ABC):
    def __init__(self, session: Session):
        super().__init__()
        self.session = session

    def init_object(self, initializable_object: UserInfoChangerBase):
        super().init_object(initializable_object)

    @abstractmethod
    def _init_something(self, jorm_changer: UserInfoChangerBase):
        pass
