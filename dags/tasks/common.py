from dags.utils.meta_class import SingletonMeta
from abc import ABC

class Extract(ABC, metaclass=SingletonMeta):
    """
    데이터 추출 : 크롤링, API, DB 등을 통한 데이터 추출
    """
    @abstractmethod
    def extract(self):
        """
        데이터 추출을 위한 추상 메소드
        """
        pass


class TransForm(ABC, metaclass=SingletonMeta):
    """
    데이터 변환 : 데이터 가공 및 분석
    """
    @abstractmethod
    def trans_form(self):
        """
        데이터 변환을 위한 추상 메소드
        """
        pass


class LoadToLake(ABC, metaclass=SingletonMeta):

    @abstractmethod
    def load_to_lake(self):
        """
        데이터 로드를 위한 추상 메소드
        """
        pass


class LoadToWareHouse(ABC, metaclass=SingletonMeta):

    @abstractmethod
    def load_to_warehouse(self):
        """
        데이터 로드를 위한 추상 메소드
        """
        pass