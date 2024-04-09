from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DBConnection:
    """
    DB세션을 연결해주는 클래스입니다.
    """
    def __init__(self, db: str):
        # .env 파일 로드
        load_dotenv("../.env")
        self.engines = {
            "api-db": create_engine(
                f'postgresql+psycopg2://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@localhost:5432/{os.getenv("POSTGRES_NAME")}'
            ),
            "airflow-db": create_engine(
                "postgresql+psycopg2://airflow:airflow@localhost:5431/airflow"
            ),
        }
        self.db_name = db
        print("DB Connection created")

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

    def __del__(self):
        self.engines["api-db"].dispose()
        self.engines["airflow-db"].dispose()


