from jorm.jarvis.db_update import UserInfoChanger, JORMChanger

from jorm.market.infrastructure import Niche
from jorm.market.person import User, Account
from jorm.market.service import Request


# TODO Implement Changers from JORM
# TODO Think about file and packages renaming
class UserInfoChangerImpl(UserInfoChanger):
    def update_session_tokens(self, old_update_token: str, new_access_token: str, new_update_token: str) -> None:
        pass

    def update_session_tokens_by_imprint(self, access_token: str, update_token: str, imprint_token: str,
                                         user: User) -> None:
        pass

    def save_all_tokens(self, access_token: str, update_token: str, imprint_token: str, user: User) -> None:
        pass

    def save_user_and_account(self, user: User, account: Account) -> None:
        pass

    def delete_tokens_for_user(self, user: User, imprint_token: str):
        pass


class JORMChangerImpl(JORMChanger):
    def save_request(self, request: Request, user: User) -> None:
        pass

    def load_new_niche(self, niche_name: str) -> Niche:
        pass
