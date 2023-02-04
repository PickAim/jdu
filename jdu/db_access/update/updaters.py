from jarvis_calc.database_interactors.db_access import DBUpdater
from jorm.market.infrastructure import Niche
from jorm.market.person import User, Account
from jorm.market.service import Request


class WildberriesDBUpdater:
    # maybe it can use wildberries providers
    pass


class CalcDBUpdater(DBUpdater):
    # TODO create me
    def save_request(self, request: Request, user: User) -> None:
        pass

    def save_all_tokens(self, access_token: str, update_token: str, imprint_token: str, user: User) -> None:
        pass

    def update_session_tokens(self, old_update_token: str, new_access_token: str, new_update_token: str) -> None:
        pass

    def update_session_tokens_by_imprint(self, access_token: str, update_token: str, imprint_token: str,
                                         user: User) -> None:
        pass

    def save_user_and_account(self, user: User, account: Account) -> None:
        pass

    def load_new_niche(self, niche_name: str) -> Niche:
        pass
