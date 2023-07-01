from jarvis_db.db_config import Base
from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker


class DbContext:
    def __init__(self, connection_sting: str = 'sqlite://', echo=False) -> None:
        if echo:
            import logging

            logging.basicConfig()
            logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
        if connection_sting.startswith("sqlite://"):
            @event.listens_for(Engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

        engine = create_engine(connection_sting)
        session = sessionmaker(bind=engine, autoflush=False)
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        self.session = session
