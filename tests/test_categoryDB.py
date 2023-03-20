import unittest

from jarvis_db import tables
from jarvis_db.db_config import Base
from jarvis_db.repositores.mappers.market.infrastructure import CategoryTableToJormMapper, NicheJormToTableMapper, \
    NicheTableToJormMapper, CategoryJormToTableMapper
from jarvis_db.repositores.market.infrastructure import CategoryRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from jdu.db_access.fill.db_fillers import WildberriesDbFiller, WildberriesDBFillerImpl
from jdu.providers.common import WildBerriesDataProviderWithoutKey
from jdu.providers.wildberries import WildBerriesDataProviderWithoutKeyImpl


class CategoryTest(unittest.TestCase):

    def setUp(self) -> None:
        engine = create_engine('sqlite://')
        session = sessionmaker(bind=engine, autoflush=False)
        Base.metadata.create_all(engine)
        marketplace_id = 1
        with session() as s, s.begin():
            s.add(tables.Marketplace(id=marketplace_id, name='marketplace1'))
        self.__session = session
        self.__marketplace_id = marketplace_id

    def test_fill_categories(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImpl()
        with self.__session() as session, session.begin():
            object_filler: WildberriesDbFiller = WildberriesDBFillerImpl(object_provider, session)
            object_filler.fill_categories(1)
        with self.__session() as session:
            repository: CategoryRepository = CategoryRepository(
                session, CategoryTableToJormMapper(NicheTableToJormMapper()),
                CategoryJormToTableMapper(NicheJormToTableMapper()))
            db_category = repository.fetch_marketplace_categories(self.__marketplace_id)
            self.assertEqual(len(db_category), 1)
