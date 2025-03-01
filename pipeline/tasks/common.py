from pipeline.utils.meta_class import SingletonMeta
from airflow.logging_config import log
import pandas as pd

class ETL(metaclass=SingletonMeta):
    def __init__(self):
        pass

    def fetch(self) -> pd.DataFrame|list:
        """
        데이터 수집(추출)
        """
        pass

    def load(self, **kwargs) -> pd.DataFrame|list:
        """
        저장
        """
        pass

    def transform(self, **kwargs) -> pd.DataFrame|list:
        """
        변환
        """
        pass

    def run(self, title: str):
        """
        추출 - 변환 - 저장 실행 함수
        """
        fetch = self.fetch()
        log.info(f" ✅ [{title}][Row: {len(fetch)}] 데이터 수집 완료 ")

        transform = self.transform(data=fetch)
        log.info(f" ✅ [{title}][Row: {len(transform)}/{len(fetch)}] 데이터 변환 완료 ")

        load = self.load(data=transform)
        log.info(f" ✅ [{title}][Row: {load}/{len(transform)}] 데이터 저장 완료 ")