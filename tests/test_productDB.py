import unittest

from jarvis_db import tables
from jarvis_db.db_config import Base
from jarvis_db.repositores.mappers.market.items import ProductTableToJormMapper, ProductJormToTableMapper
from jarvis_db.repositores.market.items import ProductCardRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from jdu.db_access.fill.db_fillers import WildberriesDbFiller, WildberriesDBFillerImpl
from jdu.providers.common import WildBerriesDataProviderWithoutKey
from jdu.providers.wildberries import WildBerriesDataProviderWithoutKeyImpl


class ProductTest(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite://')
        session = sessionmaker(bind=engine, autoflush=False)
        Base.metadata.create_all(engine)
        niche_id = 1
        with session() as s, s.begin():
            marketplace = tables.Marketplace(name='wildberries')
            category = tables.Category(
                name='Автомобильные товары', marketplace=marketplace)
            niche = tables.Niche(
                id=niche_id,
                name='niche_1',
                marketplace_commission=10,
                partial_client_commission=20,
                client_commission=30,
                return_percent=15,
                category=category
            )
            niche.products = [tables.ProductCard(
                name=f'product#{i}', article=i, cost=i * 10, ) for i in range(100, 111)]
            category.marketplace = marketplace
            s.add(marketplace)
        self.__session = session
        self.__niche_id = niche_id

    def test_add_products(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImpl()
        with self.__session() as session, session.begin():
            object_filler: WildberriesDbFiller = WildberriesDBFillerImpl(object_provider, session)
            object_filler.fill_niche_products(1, 1)
        with self.__session() as session:
            repository = ProductCardRepository(
                session, ProductTableToJormMapper(), ProductJormToTableMapper())
            db_products = repository.fetch_all_in_niche(1)
            self.assertEqual(len(db_products), 13)
