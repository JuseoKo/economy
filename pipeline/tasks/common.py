from dags.utils.meta_class import SingletonMeta
from abc import abstractmethod
import pandas as pd



class ETL(metaclass=SingletonMeta):
    def __init__(self):
        pass


    def fetch(self):
        """
        데이터 수집(추출)
        Args:
            url:
            **kwargs:

        Returns:

        """
        pass


    def load(self) -> str:
        """
        저장
        Args:
            data:

        Returns:

        """
        pass


    def transform(self) -> str:
        """
        변환
        Args:
            data:

        Returns:

        """
        pass
