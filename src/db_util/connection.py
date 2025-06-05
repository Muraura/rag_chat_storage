from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

from src.config.app_config import load_s3_config
from src.db_util.singleton_class import Singleton

CONFIG = load_s3_config()


class CommunicationsSQLAlchemyConnectionManager(metaclass=Singleton):
    engine = None
    Session = None

    def refresh_session(self):
        self.engine = create_engine(
            f'postgresql+psycopg2://{self.user}:{quote_plus(self.password)}@{self.host}/{self.database}',
            pool_size=10,
            pool_recycle=1800,
        )
        self.Session = sessionmaker(bind=self.engine)

    def __init__(self):
        self.host = CONFIG["db_host"]
        self.database = CONFIG["db_name"]
        self.user = CONFIG["db_user"]
        self.password = CONFIG["db_password"]
        self.refresh_session()


class CommunicationsSQLAlchemyConnectionManagerReadOnly(metaclass=Singleton):
    engine = None
    Session = None

    def refresh_session(self):
        self.engine = create_engine(
            f'postgresql+psycopg2://{self.user}:{quote_plus(self.password)}@{self.host}/{self.database}',
            pool_size=5,
            pool_recycle=1800,
        )
        print("dbstringghuuuu",self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def __init__(self):
        self.host = CONFIG["db_host"]
        self.database = CONFIG["db_name"]
        self.user = CONFIG["db_user"]
        self.password = CONFIG["db_password"]
        self.refresh_session()
