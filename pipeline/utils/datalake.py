from enum import Enum
import os
import pandas as pd
from datetime import datetime
from typing import Optional


class DataSource(Enum):
    """
    데이터 소스 Eunm
    """

    KRX = "krx"
    DART = "dart"


class EndPoint(Enum):
    """
    저장시 사용하는 EndPoint Enum
    """

    STOCK_LIST = "stock_list"
    STOCK_PRICE = "stock_price"
    SHORT_BALANCE = "short_balance"


class DataLake:
    """
    DataLake 저장 클래스
    """

    @staticmethod
    def get_path(date: str, endpoint: EndPoint, source: DataSource) -> str:
        """
        DataLake 저장 주소 구하는 함수
        :param date: YYYYMMDD
        :param endpoint: EndPoint()
        :param source: DataSource()
        :return:
        """
        import inspect
        import os
        # 현재 프레임의 코드 객체 가져오기
        frame = inspect.currentframe()

        # 코드 객체에서 파일 이름 추출
        filename = frame.f_code.co_filename

        # 'economy' 이전까지의 경로 추출
        result = filename.split("economy")[0] + "economy"

        # DataLake 경로 반환
        return os.path.join(
            result, date, endpoint.value, f"{source.value}.parquet"
        )

    @staticmethod
    def save_to_datalake(
        data: pd.DataFrame,
        endpoint: EndPoint,
        source: DataSource,
        date: Optional[str] = None,
    ) -> str:
        """
        Parquet 포맷 으로 데이터 저장
        :param data: 브론즈 데이터 ( 판다스 )
        :param endpoint: EndPoint()
        :param source: DataSource()
        :param date: YYYYMMDD
        :return:
        """
        if date is None:
            date = datetime.now().strftime("%Y%m%d")

        file_path = DataLake.get_path(date, endpoint, source)

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Save to parquet
        data.to_parquet(file_path, index=False)

        return file_path

    @staticmethod
    def load_from_datalake(
        endpoint: EndPoint, source: DataSource, date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        DataLake 데이터 로드
        :param endpoint: EndPoint()
        :param source: DataSource()
        :param date: YYYYMMDD
        :return:
        """
        if date is None:
            date = datetime.now().strftime("%Y%m%d")

        file_path = DataLake.get_path(date, endpoint, source)

        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Data lake file not found: {file_path}")

        # Load from parquet
        return pd.read_parquet(file_path)
