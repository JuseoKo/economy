from pipeline.utils.meta_class import SingletonMeta
from airflow.logging_config import log
import pandas as pd


class ETL(metaclass=SingletonMeta):
    def __init__(self):
        pass

    def fetch(self, **kwargs) -> pd.DataFrame | list:
        """
        데이터 수집(추출)
        """
        pass

    def load(self, **kwargs) -> pd.DataFrame | list:
        """
        저장
        """
        pass

    def transform(self, **kwargs) -> pd.DataFrame | list:
        """
        변환
        """
        pass

    def run(self, title: str):
        """
        추출 - 변환 - 저장 실행 함수
        """
        log.info(f" ⏳ [{title}] 데이터 수집 진행중..")
        fetch = self.fetch()

        log.info(f" ⏳ [{title}] 데이터 변환 진행중..")
        transform = self.transform(data=fetch)

        log.info(f" ⏳ [{title}][Row: {len(transform)}] 데이터 저장 진행중..")
        load = self.load(data=transform)

        log.info(f" ✅ [{title}][Row: {load}] 저장 완료")
        return transform
