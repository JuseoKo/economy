import pandas as pd

from pipeline.utils import utils
from pipeline.utils.meta_class import SingletonMeta
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import orm
from sqlalchemy.dialects.postgresql import insert
from contextlib import contextmanager


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

    @contextmanager
    def session_scope(self):
        """트랜잭션을 자동으로 관리하는 컨텍스트 매니저"""
        session = self.session
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


    def sync_db(self):
        """
        동기 DB 세션 반환
        """
        self.session = sessionmaker(bind=self.sync_engine, expire_on_commit=False)()
        return self.session

    def inserts(self):
        pass

    def upserts(self, table, data: pd.DataFrame, uniq_list: list, set_list: list = None, fk_table: object = None, fk_col: str = None) -> int:
        """

        table: 테이블 객체
        data : 적재할 데이터 프레임
        uniq_list : 유니크키 목록
        set_list : 업데이트할 컬럼 목록
        fk_table : FK 지정된 테이블
        fk_col : FK 지정된 컬럼


        """
        if set_list is None:
            col = set(data.columns)
            set_ = {c: getattr(insert(table).excluded, c) for c in col - set(uniq_list)}
        else:
            set_ = {c: getattr(insert(table).excluded, c) for c in set_list}

        stmt = insert(table).values(data.to_dict("records")).on_conflict_do_update(
            index_elements=uniq_list,  # 충돌 시 기준이 되는 컬럼
            set_=set_  # ucode를 제외한 모든 컬럼 업데이트
        )
        with self.session_scope() as session:
            res = session.execute(stmt)
            return res.rowcount

    def deletes(self):
        pass

    def selects(self, table, filters: dict):
        """
        데이터를 가져오는 함수
        :param table: 테이블 객체
        :param filters: 필터
            ㄴ filters = {
                'year': 2023,  # ==
                'type': {'in': ['CFS', 'OFS']},  # IN
                'period': {'like': 'Q%'},  # LIKE
                'created_at': {'between': ['2023-01-01', '2023-12-31']},  # BETWEEN
                'test1': {'ne': '1'},  # !=
                'test1': {'lt': '1'},  # <
                'test1': {'le': '1'},  # <=
                'test1': {'gt': '1'},  # >
                'test1': {'ge': '1'},  # >=
            }
        :return:
        """
        # 조건부 조회
        res = self.session.query(table).filter_by(**filters).all()

        rows = []

        for obj in res:
            # SQLAlchemy 내부 속성인 `_sa_instance_state`는 제거
            row = {
                k: v for k, v in vars(obj).items()
                if not k.startswith('_')
            }
            rows.append(row)

        df = pd.DataFrame(rows)
        return df