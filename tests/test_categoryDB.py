import unittest

from jarvis_db import tables
from jarvis_db.db_config import Base
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
            object.fill_categories()
        with self.__session() as session:
            db_categories: list[tables.Category] = session.query(
                tables.Category).all()
            for jorm_category, db_category in zip(categories, db_categories, strict=True):
                self.assertEqual(jorm_category.name, db_category.name)
