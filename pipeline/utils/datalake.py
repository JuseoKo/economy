from enum import Enum
import os
import pandas as pd
from datetime import datetime
from typing import Optional, Union


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
    PERFORMANCE_LIST = "performance_list"
    PERFORMANCE = "performance"


class DataLake:
    """
    DataLake 저장 클래스
    """

    @staticmethod
    def get_path(date: str, endpoint: EndPoint, source: DataSource, data_type: str) -> str:
        """
        DataLake 저장 주소 구하는 함수
        :param date: YYYYMMDD
        :param endpoint: EndPoint()
        :param source: DataSource()
        :param data_type: DataFrame, Text
        :return:
        """
        import inspect
        import os
        # 현재 프레임의 코드 객체 가져오기
        frame = inspect.currentframe()

        # 코드 객체에서 파일 이름 추출
        filename = frame.f_code.co_filename

        # 'economy' 이전까지의 경로 추출
        result = filename.split("economy")[0] + "economy" + "/datalake"

        # DataLake 경로 반환
        if data_type == "DataFrame":
            path = os.path.join(
                result, date, endpoint.value, f"{source.value}.parquet"
            )
        elif data_type == "Text":
            path = os.path.join(
                result, date, endpoint.value, f"{source.value}.text"
            )
        return path

    @staticmethod
    def save_to_datalake(
        data: Union[pd.DataFrame, str],
        endpoint: EndPoint,
        source: DataSource,
        date: Optional[str] = None,
        data_type: Optional[str] = "DataFrame",
    ) -> str:
        """
        Parquet 포맷 으로 데이터 저장
        :param data: 브론즈 데이터 ( 판다스 )
        :param endpoint: EndPoint()
        :param source: DataSource()
        :param date: YYYYMMDD
        :param data_type: str: DataFrame, Text
        :return:
        """
        if date is None:
            date = datetime.now().strftime("%Y%m%d")

        file_path = DataLake.get_path(date, endpoint, source, data_type)

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Save to parquet
        if data_type == "DataFrame":
            data.to_parquet(file_path, index=False)
        elif data_type == "Text":
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(data)

        return file_path

    @staticmethod
    def load_from_datalake(
        endpoint: EndPoint, source: DataSource, date: Optional[str] = None, data_type: Optional[str] = "DataFrame",
    ) -> Union[pd.DataFrame, str]:
        """
        DataLake 데이터 로드
        :param endpoint: EndPoint()
        :param source: DataSource()
        :param date: YYYYMMDD
        :param data_type: str: DataFrame, Text
        :return:
        """
        if date is None:
            date = datetime.now().strftime("%Y%m%d")

        file_path = DataLake.get_path(date, endpoint, source, data_type)

        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Data lake file not found: {file_path}")

        # Load from parquet
        if data_type == "DataFrame":
            res = pd.read_parquet(file_path)
        elif data_type == "Text":
            with open(file_path, "r", encoding="utf-8") as f:
                res = f.read()

        return res
