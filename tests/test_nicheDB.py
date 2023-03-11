import unittest
import warnings

from jarvis_db import tables as db
from jarvis_db.db_config import Base
from jarvis_db.repositores.mappers.market.infrastructure import NicheTableToJormMapper, NicheJormToTableMapper, \
    CategoryTableToJormMapper, CategoryJormToTableMapper
from jarvis_db.repositores.market.infrastructure import NicheRepository, CategoryRepository
from jorm.market.infrastructure import Category
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from jdu.db_access.fill.db_fillers import WildberriesDbFiller, WildberriesDBFillerImpl
from jdu.db_access.update.updaters import CalcDBUpdater
from jdu.providers.common import WildBerriesDataProviderWithoutKey
from jdu.providers.wildberries import WildBerriesDataProviderWithoutKeyImpl

warnings.filterwarnings(action="ignore", message="ResourceWarning: unclosed")


class NicheTest(unittest.TestCase):
    def setUp(self) -> None:
        engine = create_engine('sqlite://')
        session = sessionmaker(bind=engine, autoflush=False)
        Base.metadata.create_all(engine)
        marketplace_name = 'wildberries'
        db_marketpace = db.Marketplace(name=marketplace_name)
        category_name = 'Автомобильные товары'
        db_category1 = db.Category(
            name=category_name, marketplace=db_marketpace)
        db_category2 = db.Category(name='otherCategory', marketplace=db_marketpace)
        with session() as s, s.begin():
            s.add(db_category1)
            s.add(db_category2)
        self.__marketplace_name = marketplace_name
        self.__category_name = category_name
        self.__session = session

    def test_fill_niches(self):
        niche_name = 'AKF системы'
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImpl()
        with self.__session() as session, session.begin():
            object: WildberriesDbFiller = WildberriesDBFillerImpl(object_provider, session)
            object.fill_niches(1, 1)
        with self.__session() as session:
            category_repository = CategoryRepository(
                session, CategoryTableToJormMapper(NicheTableToJormMapper()),
                CategoryJormToTableMapper(NicheJormToTableMapper()))
            categories: list[Category] = category_repository.fetch_marketplace_categories(self.__marketplace_name)
            db_niche = list(categories[0].niches.keys())[0].__str__()
            self.assertEqual(db_niche, niche_name)

    def test_add_niche_by_category_name(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImpl()
        niche_name = 'AKF системы'
        with self.__session() as session, session.begin():
            db_updater = CalcDBUpdater(object_provider, session)
            db_updater.load_new_niche(niche_name)
        with self.__session() as session:
            repository = NicheRepository(
                session, NicheTableToJormMapper(), NicheJormToTableMapper())
            db_niche = repository.fetch_niches_by_category('otherCategory', self.__marketplace_name)
            self.assertEqual(len(db_niche), 1)
