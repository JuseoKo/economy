import pandas as pd
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy import orm
from tasks.utils.singleton import SingletonMeta
from airflow.logging_config import log

from sqlalchemy.dialects.postgresql import insert

Base = orm.declarative_base()


class DBConnection(metaclass=SingletonMeta):
    """
    DB세션을 연결해주는 클래스입니다.
    """

    def __init__(self, db: str):
        # .env 파일 로드
        current_path = os.getcwd()
        # alembic 명령어시 path
        alembic_path = os.path.dirname(os.path.dirname(current_path))
        # airflow에서 ORM으로 사용하는 path
        orm_path = os.path.dirname(alembic_path)

        if load_dotenv(f"{alembic_path}/.env"):
            pass
        else:
            load_dotenv(f"{orm_path}/.env")

        self.engines = {
            "api": create_engine(
                f'postgresql+psycopg2://{os.getenv("API_USER")}:{os.getenv("API_PASSWORD")}@{os.getenv("API_HOST")}:5432/{os.getenv("API_NAME")}'
            ),
            "airflow": create_engine(
                f'postgresql+psycopg2://{os.getenv("AIRFLOW_USER")}:{os.getenv("AIRFLOW_PASSWORD")}@{os.getenv("AIRFLOW_POSTGRES_HOST")}:5431/{os.getenv("AIRFLOW_NAME")}'
            ),
        }
        self.db_name = db
        log.info(f"[DB: {db}]Connection created")
        log.info(f"URL: {self.engines[db]}")

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

    def pg_bulk_upsert(
        self, session, df: pd.DataFrame, model, uniq_key: list, batch_size: int = 100
    ) -> int:
        """
        데이터프레임을 bulk_upsert 하는 함수입니다.
        :param session:
        :param df:
        :param model: sql알케미 모델
        :param uniq_key:
        :return:
        """
        # 모델의 컬럼 이름을 가져옵니다.
        model_columns = [c.name for c in model.__table__.columns]

        # 데이터프레임의 컬럼 이름을 가져옵니다.
        df_columns = df.columns.tolist()
        cnt = 0
        for start in range(0, len(df), batch_size):
            # 데이터프레임을 딕셔너리로 변환합니다.
            data = df.iloc[start : start + batch_size].to_dict(orient="records")

            # PostgreSQL upsert 문을 생성합니다.
            stmt = insert(model).values(data)

            # 충돌 시 업데이트할 필드를 설정합니다.
            # 데이터프레임 컬럼과 모델 컬럼 간의 차이를 처리합니다.
            update_dict = {
                col: insert(model).excluded[col]
                for col in df_columns
                if col in model_columns and col not in uniq_key
            }

            update_stmt = stmt.on_conflict_do_update(
                index_elements=uniq_key, set_=update_dict
            )
            # 쿼리를 실행합니다.
            session.execute(update_stmt)
            cnt += len(data)
        session.commit()
        return cnt

    def __del__(self):
        self.engines["api"].dispose()
        self.engines["airflow"].dispose()
