import os
from contextlib import contextmanager

import pandas as pd
from sqlalchemy import and_, create_engine, func, orm
from sqlalchemy.dialects.postgresql import (
    insert as pg_insert,
)  # PG 전용 insert 사용 권장
from sqlalchemy.orm import sessionmaker

from pipeline.utils import utils
from pipeline.utils.meta_class import SingletonMeta

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
            f"postgresql+psycopg2://{os.getenv('API_USER')}:{os.getenv('API_PASSWORD')}@{os.getenv('API_HOST')}:5432/{os.getenv('API_NAME')}"
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

    def upserts(
        self,
        table,
        data: pd.DataFrame,
        uniq_list: list,
        set_list: list = None,
        fk_table: object = None,
        fk_col: str = None,
    ) -> int:
        """

        table: 테이블 객체
        data : 적재할 데이터 프레임
        uniq_list : 유니크키 목록
        set_list : 업데이트할 컬럼 목록
        fk_table : FK 지정된 테이블
        fk_col : FK 지정된 컬럼
        """
        if data is None or data.empty:
            return 0

        records = data.to_dict("records")

        ins = pg_insert(table).values(records)
        excluded = ins.excluded  # EXCLUDED 별칭 재사용

        # 업데이트 대상 컬럼 결정
        if set_list is None:
            update_cols = [
                c
                for c in data.columns
                if c not in uniq_list and c not in ("created_at", "updated_at")
            ]
        else:
            update_cols = [
                c
                for c in set_list
                if c not in uniq_list and c not in ("created_at", "updated_at")
            ]

        # EXCLUDED 값으로 갱신 + updated_at은 항상 now()로
        set_dict = {c: getattr(excluded, c) for c in update_cols}
        set_dict["updated_at"] = func.now()

        stmt = ins.on_conflict_do_update(
            index_elements=uniq_list,
            set_=set_dict,
            # (옵션) 특정 조건에서만 업데이트하고 싶으면 where= 추가 가능
            # where=(table.c.some_flag.is_(True))
        )

        with self.session_scope() as session:
            res = session.execute(stmt)
            return res.rowcount

    def deletes(self):
        pass

    def selects(self, table, *conditions) -> pd.DataFrame:
        """
        스마트한 SQLAlchemy 조건 기반 조회
        :param table: SQLAlchemy 모델
        :param conditions: SQLAlchemy 조건 표현식 (ex. table.col == value, col.in_(...), ...)
        :return: pandas DataFrame
        """
        query = self.session.query(table)

        if conditions:
            query = query.filter(and_(*conditions))

        res = query.all()

        rows = [
            {k: v for k, v in vars(obj).items() if not k.startswith("_")} for obj in res
        ]
        return pd.DataFrame(rows)
