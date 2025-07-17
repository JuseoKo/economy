"""
데이터 소스 http://data.krx.co.kr/contents/MDC/MAIN/main/index.cmd
"""

import pandas as pd
from pipeline.utils import preprocessing
from pipeline.utils.default_request import Request
from pipeline.tasks.common import ETL
from pipeline.table.models.stock.dim_company import CompanyDimension
from pipeline.table.models.stock.fact_price import FactStockPrice
from pipeline.table.base import DBConnection
from pipeline.utils.datalake import DataLake, DataSource, EndPoint


class KrxBase(ETL):
    def __init__(self):
        super().__init__()
        self.request = Request()
        self.db = DBConnection()
        self.url = "http://data.krx.co.kr/"
        self.headers = {
            "Accept": "application/json, text/javascript, */*; q = 0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
            "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "data.krx.co.kr",
            "Origin": "http://data.krx.co.kr",
            "Referer": "http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?",
        }


class StockList(KrxBase):
    """
    KRX의 주식 목록을 가져오는 클래스
    http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC02030101
    """

    def __init__(self):
        super().__init__()

    def fetch(self) -> pd.DataFrame:
        """
        Returns: 원본 상장사 목록
        """
        url = f"{self.url}/comm/bldAttendant/getJsonData.cmd"
        payload = {
            "bld": "dbms/MDC/STAT/standard/MDCSTAT01901",
            "locale": "ko_KR",
            "mktId": "ALL",
            "share": "1",
            "csvxls_isNo": "false",
        }
        self.headers.update({"Content-length": "88"})
        res = self.request.post(url=url, data=payload, headers=self.headers)

        # API 호출 결과를 DataFrame으로 변환
        data = pd.DataFrame(res.json()["OutBlock_1"])

        # data lake 저장
        from datetime import datetime

        date = datetime.now().strftime("%Y%m%d")
        DataLake.save_to_datalake(
            data=data, endpoint=EndPoint.STOCK_LIST, source=DataSource.KRX, date=date
        )

        return data

    def transform(self, data: pd.DataFrame = None, **kwargs) -> pd.DataFrame:
        """
        한국 거래소(KRX)의 상장사 목록을 처리하는 함수
        :param data:
        :param kwargs:
        :return:
        """
        # 데이터가 없으면 데이터 레이크에서 로드
        if data is None:
            from datetime import datetime

            date = kwargs.get("date", datetime.now().strftime("%Y%m%d"))
            data = DataLake.load_from_datalake(
                endpoint=EndPoint.STOCK_LIST, source=DataSource.KRX, date=date
            )

        # 데이터 변환
        data["type"] = "STOCK"
        data["country"] = "KR"
        data["is_yn"] = "Y"

        data.rename(
            columns={
                "ISU_CD": "isin",
                "ISU_NM": "kr_name",
                "ISU_ENG_NM": "us_name",
                "MKT_TP_NM": "market",
                "ISU_SRT_CD": "symbol",
            },
            inplace=True,
        )
        data["ucode"] = data.apply(
            lambda x: preprocessing.create_ucode(x["country"], x["symbol"]), axis=1
        )
        data = data[
            [
                "type",
                "country",
                "is_yn",
                "isin",
                "kr_name",
                "us_name",
                "market",
                "symbol",
                "ucode",
            ]
        ]
        return data

    def load(self, data: pd.DataFrame):
        """
        데이터 저장
        :param data:
        :return:
        """
        uniq = ["ucode"]
        res = self.db.upserts(CompanyDimension, data, uniq)
        return res


class StockPrice(KrxBase):
    """
    KRX의 주가를 가져오는 클래스
    http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC02030101
    """

    def __init__(self):
        super().__init__()

    def fetch(self, get_date: str = None, **kwargs) -> pd.DataFrame:
        """
        주가 목록을 가져오는 함수
        :param get_date: YYYYMMDD
        :param kwargs:
        :return:
        """
        # 1. 설정
        if get_date is None:
            from datetime import datetime

            get_date = datetime.now().strftime("%Y%m%d")

        url = f"{self.url}comm/bldAttendant/getJsonData.cmd"
        payload = {
            "bld": "dbms/MDC/STAT/standard/MDCSTAT01501",
            "trdDd": get_date,
            "locale": "ko_KR",
            "mktId": "ALL",
            "share": "1",
            "money": "1",
            "csvxls_isNo": "false",
        }
        self.headers.update({"Content-length": "111"})

        # 2. API 호출
        res = self.request.post(url=url, data=payload, headers=self.headers)

        # 3. 결과를 DataFrame으로 변환
        data = pd.DataFrame(res.json()["OutBlock_1"])

        # 4. 데이터 레이크에 저장
        DataLake.save_to_datalake(
            data=data,
            endpoint=EndPoint.STOCK_PRICE,
            source=DataSource.KRX,
            date=get_date,
        )

        # 5. 결과 반환
        return data

    def transform(self, data: pd.DataFrame = None, **kwargs):
        """
        주가 데이터를 처리하는 함수
        :param data:
        :param kwargs:
        :return:
        """
        # 데이터가 없으면 데이터 레이크에서 로드
        if data is None:
            get_date = kwargs.get("params", {}).get("get_date")
            if get_date is None:
                from datetime import datetime

                get_date = datetime.now().strftime("%Y%m%d")

            data = DataLake.load_from_datalake(
                endpoint=EndPoint.STOCK_PRICE, source=DataSource.KRX, date=get_date
            )

        # 1. 데이터 추가
        get_date = kwargs.get("params", {}).get("get_date")
        if get_date is None:
            from datetime import datetime

            get_date = datetime.now().strftime("%Y%m%d")

        data["ucode"] = data.apply(
            lambda x: preprocessing.create_ucode("KR", x["ISU_SRT_CD"]), axis=1
        )
        data["date"] = pd.to_datetime(get_date, format="%Y%m%d").date()

        # 2. 컬럼명 변경
        data.rename(
            columns={
                "MKTCAP": "mkt_cap",
                "TDD_CLSPRC": "price",
                "ACC_TRDVOL": "volume",
                "LIST_SHRS": "list_shrs",
            },
            inplace=True,
        )

        # 3. 전처리 (, 제거 )
        data["mkt_cap"] = data["mkt_cap"].str.replace(",", "")
        data["price"] = data["price"].str.replace(",", "")
        data["volume"] = data["volume"].str.replace(",", "")
        data["list_shrs"] = data["list_shrs"].str.replace(",", "")
        data = data[["ucode", "date", "mkt_cap", "price", "volume", "list_shrs"]]
        return data

    def load(self, data: pd.DataFrame):
        """
        주가 데이터를 데이터베이스에 저장하는 함수
        :param data:
        :return:
        """
        uniq = ["ucode", "date"]
        res = self.db.upserts(FactStockPrice, data, uniq)
        return res


class StockShortBalance(KrxBase):
    """
    KRX의 공매도 잔고 데이터를 가져오는 클래스
    http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC02030301
    """

    def __init__(self):
        super().__init__()

    def fetch(self, get_date: str = None, **kwargs) -> pd.DataFrame:
        """
        Returns: 원본 공매도 잔고 데이터

        Args:
            get_date: YYYYMMDD format date
            **kwargs: Additional parameters
        """
        # This is a placeholder for the actual implementation
        # When implemented, it should follow this pattern:

        # 1. Get data from API
        # data = ... (API call)

        # 2. Save to data lake
        # if get_date is None:
        #     from datetime import datetime
        #     get_date = datetime.now().strftime("%Y%m%d")
        #
        # DataLake.save_to_datalake(
        #     data=data,
        #     endpoint=EndPoint.SHORT_BALANCE,
        #     source=DataSource.KRX,
        #     date=get_date
        # )

        # Return empty DataFrame for now
        return pd.DataFrame()

    def transform(self, data: pd.DataFrame = None, **kwargs):
        """
        Returns: 처리된 공매도 잔고 데이터

        Args:
            data: Optional DataFrame (if None, loads from data lake)
            **kwargs: Additional parameters
        """
        # This is a placeholder for the actual implementation
        # When implemented, it should follow this pattern:

        # 1. Load data from data lake if not provided
        # if data is None:
        #     get_date = kwargs.get('params', {}).get('get_date')
        #     if get_date is None:
        #         from datetime import datetime
        #         get_date = datetime.now().strftime("%Y%m%d")
        #
        #     data = DataLake.load_from_datalake(
        #         endpoint=EndPoint.SHORT_BALANCE,
        #         source=DataSource.KRX,
        #         date=get_date
        #     )

        # 2. Process data
        # ...

        # Return empty DataFrame for now
        return pd.DataFrame()

    def load(self, data: pd.DataFrame):
        """
        Returns: 저장된 상장사 목록
        """
        pass
