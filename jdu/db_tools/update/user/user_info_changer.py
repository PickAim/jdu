from typing import Type

from jorm.market.person import Account, User
from sqlalchemy.orm import Session

from jdu.db_tools.update.user.base import UserInfoChangerBase
from jdu.db_tools.update.user.initializers import UserInfoChangerInitializer


class UserInfoChangerImpl(UserInfoChangerBase):
    def __init__(self, session: Session, initializer_class: Type[UserInfoChangerInitializer]):
        super().__init__()
        initializer_class(session).init_object(self)

    def update_session_tokens(
            self,
            user_id: int,
            old_update_token: str,
            new_access_token: str,
            new_update_token: str,
    ) -> None:
        self.token_service.update_by_access(
            user_id, old_update_token, new_access_token, new_update_token
        )

    def update_session_tokens_by_imprint(
            self, access_token: str, update_token: str, imprint_token: str, user_id: int
    ) -> None:
        self.token_service.update_by_imprint(
            user_id, access_token, update_token, imprint_token
        )

    def add_marketplace_api_key(self, api_key: str, user_id: int, marketplace_id: int) -> None:
        self.user_service.append_api_key(user_id, api_key, marketplace_id)

    def save_all_tokens(
            self, access_token: str, update_token: str, imprint_token: str, user_id: int
    ) -> None:
        self.token_service.create(user_id, access_token, update_token, imprint_token)

    def save_user_and_account(self, user: User, account: Account) -> None:
        self.account_service.create(account)
        _, account_id = self.account_service.find_by_email(account.email)
        self.user_service.create(user, account_id)

    def delete_marketplace_api_key(self, user_id: int, marketplace_id: int) -> None:
        pass

    def delete_account(self, user_id: int) -> None:
        pass

    def delete_tokens_for_user(self, user_id: int, imprint_token: str) -> None:
        self.token_service.delete_by_imprint(user_id, imprint_token)
