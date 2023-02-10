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
        marketplace_name = 'wildberries'
        category_name = 'Автомобильные товары'
        niche_name = 'AKF системы'
        with session() as s, s.begin():
            marketplace = tables.Marketplace(name=marketplace_name)
            category = tables.Category(name=category_name)
            niche = tables.Niche(
                name=niche_name,
                marketplace_commission=10,
                partial_client_commission=20,
                client_commission=30,
                return_percent=15
            )
            niche.category = category
            object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImpl()
            products = object_provider.get_products_by_niche("Аварийное оборудование", 1)
            niche.products = [tables.ProductCard(
                name=products[0].name, article=products[0].article, cost=products[0].cost)]

            category.marketplace = marketplace
            s.add(marketplace)
        self.__session = session
        self.__marketplace_name = marketplace_name
        self.__category_name = category_name
        self.__niche_name = niche_name

    def test_add_products(self):
        object_provider: WildBerriesDataProviderWithoutKey = WildBerriesDataProviderWithoutKeyImpl()
        with self.__session() as session, session.begin():
            object: WildberriesDbFiller = WildberriesDBFillerImpl(object_provider, session)
            object.fill_niche_products()
        with self.__session() as session:
            repository = ProductCardRepository(
                session, ProductTableToJormMapper(), ProductJormToTableMapper())
            db_products = repository.fetch_all_in_niche(self.__niche_name, self.__category_name,
                                                        self.__marketplace_name)
            # for product, db_product in zip(products, db_products, strict=True):
            #     self.assertEqual(db_product.name, product.name)
            #     self.assertEqual(db_product.cost, product.cost)
            #     self.assertEqual(db_product.article, product.article)
            print(db_products)
