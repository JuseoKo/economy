from typing import Any
from pipeline.utils.meta_class import SingletonMeta
from airflow.logging_config import log


class ELT(metaclass=SingletonMeta):
    def __init__(self):
        pass

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

    def fetch(self, **kwargs) -> Any:
        """
        데이터 수집(추출)
        """
        pass

    def transform(self, **kwargs) -> Any:
        """
        변환
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

