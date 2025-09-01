from typing import Any

import requests
from airflow.logging_config import log

from pipeline.utils.datalake import DataLake, DataSource, EndPoint
from pipeline.utils.meta_class import SingletonMeta


class ELT(metaclass=SingletonMeta):
    DataLake: DataLake = DataLake()
    DataSource: DataSource = DataSource
    EndPoint: EndPoint = EndPoint

    def __init__(self):
        pass

    # ====== Extract ======
    def fetch(self, **kwargs) -> Any:
        """
        데이터 수집(추출)
        """
        # 1. 데이터 수집
        self._get_request()

        # 2. 데이터 적재 To DataLake
        self._load_to_datalake()

    def _get_request(self, **kwargs) -> requests.Response:
        pass

    # ====== Transform ======
    def transform(self, **kwargs) -> Any:
        # 1. 데이터 불러오기
        self._load_to_datalake()

        # 2. 데이터 처리
        self._preprocessing()

        # 3. 데이터 저장
        self._load_to_db()

    def _preprocessing(self, **kwargs) -> Any:
        pass

    # ====== Load ======
    def _load_to_datalake(self, **kwargs) -> Any:
        """
        DB 저장
        """
        pass

    def _load_to_db(self, **kwargs) -> Any:
        """
        DB 저장
        """
        pass

    def run(self, title: str, **kwargs):
        """
        ELT 실행 함수
        """
        log.info(f" ⏳ [{title}] 데이터 수집 진행중..")
        load_cnt = self.fetch(**kwargs)
        log.info(f" ✅ [{title}][Row: {load_cnt}] 수집 완료")

        log.info(f" ⏳ [{title}] 데이터 변환 진행중..")
        save_cnt = self.transform(**kwargs)
        log.info(f" ✅ [{title}][Row: {save_cnt}] 저장 완료")
