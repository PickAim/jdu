import unittest
import warnings

from jarvis_db import tables
from jarvis_db.db_config import Base
from jarvis_db.repositores.mappers.market.infrastructure import NicheTableToJormMapper, NicheJormToTableMapper
from jarvis_db.repositores.market.infrastructure import NicheRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from jdu.db_access.fill.db_fillers import WildberriesDbFiller, WildberriesDBFillerImpl
from jdu.providers.common import WildBerriesDataProviderWithoutKey
from jdu.providers.wildberries import WildBerriesDataProviderWithoutKeyImpl

warnings.filterwarnings(action="ignore", message="ResourceWarning: unclosed")


class NicheTest(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite://')
        session = sessionmaker(bind=engine, autoflush=False)
        Base.metadata.create_all(engine)
        category_id = 1
        db_marketplace = tables.Marketplace(name='wildberries')
        db_category = tables.Category(
            id=category_id, name='Автомобильные товары', marketplace=db_marketplace)
        with session() as s, s.begin():
            s.add(db_category)
        self.__category_id = category_id
        self.__session = session

    def test_fill_niches(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImpl()
        with self.__session() as session, session.begin():
            object_filler: WildberriesDbFiller = WildberriesDBFillerImpl(object_provider, session)
            object_filler.fill_niches(1)
        with self.__session() as session:
            repository = NicheRepository(
                session, NicheTableToJormMapper(), NicheJormToTableMapper())
            db_niche = repository.fetch_niches_by_category(1)
            self.assertEqual(len(db_niche), 1)
