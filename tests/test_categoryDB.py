import unittest

from jarvis_db import tables
from jarvis_db.db_config import Base
from jarvis_db.repositores.mappers.market.infrastructure import CategoryTableToJormMapper, NicheJormToTableMapper, \
    NicheTableToJormMapper, CategoryJormToTableMapper
from jarvis_db.repositores.market.infrastructure import CategoryRepository
from jorm.market.infrastructure import Category
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
        marketplace_name = 'wildberries'
        with session() as s, s.begin():
            s.add(tables.Marketplace(name=marketplace_name))
        self.__marketplace_name = marketplace_name
        self.__session = session

    def test_fill_categories(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImpl()
        categories = object_provider.get_categories(1, 1, 1)
        with self.__session() as session, session.begin():
            object: WildberriesDbFiller = WildberriesDBFillerImpl(object_provider, session)
            object.fill_categories(1, 1, 1)
        with self.__session() as session:
            category_repository = CategoryRepository(
                session, CategoryTableToJormMapper(NicheTableToJormMapper()),
                CategoryJormToTableMapper(NicheJormToTableMapper()))
            db_categories: list[Category] = category_repository.fetch_marketplace_categories(self.__marketplace_name)
            print(db_categories)
            for jorm_category, db_category in zip(categories, db_categories, strict=True):
                self.assertEqual(jorm_category, db_category)
