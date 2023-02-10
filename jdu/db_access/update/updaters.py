from jarvis_calc.database_interactors.db_access import DBUpdater
from jarvis_db.repositores.mappers.market.infrastructure import NicheTableToJormMapper, NicheJormToTableMapper
from jarvis_db.repositores.market.infrastructure import NicheRepository
from jorm.market.infrastructure import Niche, HandlerType
from jorm.market.person import User, Account
from jorm.market.service import Request
from sqlalchemy.orm import Session

from jdu.providers.common import WildBerriesDataProviderWithoutKey


class CalcDBUpdater(DBUpdater):
    def __init__(self, provider: WildBerriesDataProviderWithoutKey, session: Session):
        super().__init__()
        self.marketplace_name = 'wildberries'
        self.__provider = provider
        self.__session = session

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
        repository = NicheRepository(
            self.__session, NicheTableToJormMapper(), NicheJormToTableMapper())
        repository.add_by_category_name(Niche(niche_name, {
            HandlerType.MARKETPLACE: 0,
            HandlerType.PARTIAL_CLIENT: 0,
            HandlerType.CLIENT: 0},
                                              0, self.__provider.get_products_by_niche(niche_name, 1)), 'otherCategory',
                                        self.marketplace_name)
        return Niche(niche_name, {
            HandlerType.MARKETPLACE: 0,
            HandlerType.PARTIAL_CLIENT: 0,
            HandlerType.CLIENT: 0},
                     0, self.__provider.get_products_by_niche(niche_name, 1))
