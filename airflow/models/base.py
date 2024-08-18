import pandas as pd
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import logging
from sqlalchemy import orm

from sqlalchemy.dialects.postgresql import insert
Base = orm.declarative_base()

class DBConnection:
    """
    DB세션을 연결해주는 클래스입니다.
    """
    def __init__(self, db: str):
        # .env 파일 로드
        current_path = os.getcwd()
        parent_path = os.path.dirname(current_path)
        two_parents_path = os.path.dirname(parent_path)
        if load_dotenv(f"{two_parents_path}/.env"):
            pass
        else:
            load_dotenv(f".env")
        self.engines = {
            "api": create_engine(
                f'postgresql+psycopg2://{os.getenv("API_USER")}:{os.getenv("API_PASSWORD")}@{os.getenv("API_HOST")}:5432/{os.getenv("API_NAME")}'
            ),
            "airflow": create_engine(
                f'postgresql+psycopg2://{os.getenv("AIRFLOW_USER")}:{os.getenv("AIRFLOW_PASSWORD")}@{os.getenv("AIRFLOW_POSTGRES_HOST")}:5431/{os.getenv("AIRFLOW_NAME")}'
            ),
        }
        self.db_name = db
        logging.info(f"[DB: {db}]Connection created")
        logging.info(f"URL: {self.engines[db]}")

    def create_session(self):
        """
        sqlalchemy session 반환
        :param db: api-db or airflow-db
        :return:
        """
        return sessionmaker(bind=self.engines[self.db_name])()

    def get_url(self):
        """
        url 반환
        :param db: api-db or airflow-db
        :return:
        """
        return self.engines[self.db_name].url

    def pg_bulk_upsert(self, session, df: pd.DataFrame, model, uniq_key: list):
        """
        데이터프레임을 bulk_upsert 하는 함수입니다.
        :param session:
        :param df:
        :param model:
        :param uniq_key:
        :return:
        """
        obj_list = df.to_dict("records")
        for item in obj_list:
            stmt = insert(model).values(item)
            stmt = stmt.on_conflict_do_update(
                index_elements=uniq_key, set_=item
            )
            session.execute(stmt)

        session.commit()
        session.close()

    def __del__(self):
        self.engines["api"].dispose()
        self.engines["airflow"].dispose()


