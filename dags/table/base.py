from dags.utils import utils
from dags.utils.meta_class import SingletonMeta
import os
import logging
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import orm

Base = orm.declarative_base()


class DBConnection(metaclass=SingletonMeta):
    """
    DB세션을 연결해주는 클래스입니다.
    """

    def __init__(self):
        # env load
        utils.setings_env()

        # 동기 엔진
        self.sync_engine = create_engine(
            f'postgresql+psycopg2://{os.getenv("API_USER")}:{os.getenv("API_PASSWORD")}@{os.getenv("API_HOST")}:5432/{os.getenv("API_NAME")}'
        )
        self.sync_session = sessionmaker(bind=self.sync_engine, expire_on_commit=False)

        logging.info(f"engines created")
        logging.info(f"URL: {self.sync_engine.url}")

    def sync_db(self):
        """
        동기 DB 세션 반환
        """
        return self.sync_session()