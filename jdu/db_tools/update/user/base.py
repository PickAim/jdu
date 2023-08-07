from abc import ABC

from jarvis_db.services.market.person import UserService, AccountService, TokenService
from jorm.jarvis.db_update import UserInfoChanger
from jorm.jarvis.initialization import Initializable


class UserInfoChangerBase(UserInfoChanger, Initializable, ABC):
    def __init__(self):
        self.user_service: UserService | None = None
        self.account_service: AccountService | None = None
        self.token_service: TokenService | None = None
