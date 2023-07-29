from jarvis_db.services.market.person.account_service import AccountService
from jarvis_db.services.market.person.token_service import TokenService
from jarvis_db.services.market.person.user_service import UserService
from jorm.jarvis.db_update import UserInfoChanger
from jorm.market.infrastructure import Warehouse
from jorm.market.items import Product
from jorm.market.person import Account, User


class UserInfoChangerImpl(UserInfoChanger):
    def __init__(
            self,
            user_service: UserService,
            account_service: AccountService,
            token_service: TokenService,
    ):
        self.__user_service = user_service
        self.__account_service = account_service
        self.__token_service = token_service

    def update_session_tokens(
            self,
            user_id: int,
            old_update_token: str,
            new_access_token: str,
            new_update_token: str,
    ) -> None:
        self.__token_service.update_by_access(
            user_id, old_update_token, new_access_token, new_update_token
        )

    def update_session_tokens_by_imprint(
            self, access_token: str, update_token: str, imprint_token: str, user_id: int
    ) -> None:
        self.__token_service.update_by_imprint(
            user_id, access_token, update_token, imprint_token
        )

    def add_marketplace_api_key(self, api_key: str, user_id: int, marketplace_id: int) -> None:
        self.__user_service.append_api_key(user_id, api_key, marketplace_id)

    def save_all_tokens(
            self, access_token: str, update_token: str, imprint_token: str, user_id: int
    ) -> None:
        self.__token_service.create(user_id, access_token, update_token, imprint_token)

    def save_user_and_account(self, user: User, account: Account) -> None:
        self.__account_service.create(account)
        _, account_id = self.__account_service.find_by_email(account.email)
        self.__user_service.create(user, account_id)

    def delete_marketplace_api_key(self, user_id: int, marketplace_id: int) -> None:
        pass

    def delete_account(self, user_id: int) -> None:
        pass

    def delete_tokens_for_user(self, user_id: int, imprint_token: str) -> None:
        self.__token_service.delete_by_imprint(user_id, imprint_token)