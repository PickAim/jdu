from jarvis_calc.database_interactors.db_access import DBUpdater
from jarvis_db.repositores.mappers.market.infrastructure import NicheTableToJormMapper, NicheJormToTableMapper, \
    CategoryTableToJormMapper, CategoryJormToTableMapper
from jarvis_db.repositores.market.infrastructure import NicheRepository, CategoryRepository
from jorm.market.infrastructure import Niche, HandlerType, Category
from jorm.market.person import User, Account
from jorm.market.service import Request
from sqlalchemy.orm import Session

from jdu.providers.common import WildBerriesDataProviderWithoutKey


class CalcDBUpdater(DBUpdater):
    def delete_tokens_for_user(self, user_id: int, imprint_token: str):
        pass

    def __init__(self, provider: WildBerriesDataProviderWithoutKey, session: Session):
        self.__marketplace_name = provider.marketplace_name
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
        category_repository = CategoryRepository(
            self.__session, CategoryTableToJormMapper(NicheTableToJormMapper()),
            CategoryJormToTableMapper(NicheJormToTableMapper()))
        categories: list[Category] = category_repository.fetch_marketplace_categories(self.__marketplace_name)
        categories_name: list[str] = []
        for element in categories:
            categories_name.append(element.name)
        if 'otherCategory' not in categories_name:
            category_repository.add_category_to_marketplace(Category('otherCategory'), self.__marketplace_name)
        niche_repository = NicheRepository(
            self.__session, NicheTableToJormMapper(), NicheJormToTableMapper())
        new_niche: Niche = Niche(niche_name, {
            HandlerType.MARKETPLACE: 0,
            HandlerType.PARTIAL_CLIENT: 0,
            HandlerType.CLIENT: 0},
                                 0, self.__provider.get_products_by_niche(niche_name))
        niche_repository.add_by_category_name(new_niche, 'otherCategory', self.__marketplace_name)
        return new_niche
