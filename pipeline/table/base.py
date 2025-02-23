import pandas as pd

from pipeline.utils import utils
from pipeline.utils.meta_class import SingletonMeta
import os
import logging
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import orm
from sqlalchemy.dialects.postgresql import insert

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
        self.session = self.sync_db()

        logging.info(f"engines created")
        logging.info(f"URL: {self.sync_engine.url}")

    def sync_db(self):
        """
        동기 DB 세션 반환
        """
        self.session = sessionmaker(bind=self.sync_engine, expire_on_commit=False)()
        return self.session

    def inserts(self):
        pass

    def upserts(self, table, data: pd.DataFrame, uniq_list: list, set_list: list = None) -> int:
        if set_list is None:
            col = set(data.columns)
            set_ = {c: getattr(insert(table).excluded, c) for c in col - set(uniq_list)}
        else:
            set_ = {c: getattr(insert(table).excluded, c) for c in set_list}

        stmt = insert(table).values(data.to_dict("records")).on_conflict_do_update(
            index_elements=uniq_list,  # 충돌 시 기준이 되는 컬럼
            set_=set_  # ucode를 제외한 모든 컬럼 업데이트
        )
        res = self.session.execute(stmt)
        self.session.commit()
        return res.rowcount

    def deletes(self):
        pass

    def selects(self):
        pass