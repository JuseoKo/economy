"""
데이터 소스 http://data.krx.co.kr/contents/MDC/MAIN/main/index.cmd
"""

import pandas as pd
import requests

from pipeline.utils import preprocessing
from pipeline.utils.default_request import Request
from pipeline.tasks.common import ELT
from pipeline.table.models.stock.dim_company import CompanyDimension
from pipeline.table.models.stock.fact_price import FactStockPrice
from pipeline.table.base import DBConnection
from pipeline.utils.datalake import DataLake, DataSource, EndPoint


class KrxBase(ELT):
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

    def fetch(self, **kwargs) -> int:
        """
        Returns: 원본 상장사 목록
        """

        # 1. KRX 상장사 목록 API 호출
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

        # 2. 데이터 레이크에 저장
        save_cnt = self._load_to_datalake(res)

        return save_cnt

    def _load_to_datalake(self, data: pd.DataFrame) -> int:
        """
        KRX 상장사 목록을 데이터 레이크에 저장
        :param data:
        :return:
        """
        # 2. API 호출 결과를 DataFrame으로 변환
        data = pd.DataFrame(data.json()["OutBlock_1"])

        # 3. data lake 저장
        DataLake.save_to_datalake(
            data=data, endpoint=EndPoint.STOCK_LIST, source=DataSource.KRX, date=None
        )
        return len(data)

    def transform(self, **kwargs) -> int:
        """
        한국 거래소(KRX)의 상장사 목록을 처리하는 함수
        """
        # 1. 데이터 레이크 로드
        data = DataLake.load_from_datalake(
            endpoint=EndPoint.STOCK_LIST, source=DataSource.KRX, date=None
        )

        # 2. 데이터 변환
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

        # 3. DB에 저장
        cnt = self._load_to_db(data)

        return cnt

    def _load_to_db(self, data: pd.DataFrame):
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

    def _load_to_db(self, data: pd.DataFrame):
        """
        :param data: 최종 주가 데이터
        :return:
        """
        uniq = ["ucode", "date"]
        save_cnt = self.db.upserts(FactStockPrice, data, uniq)
        return save_cnt

    def fetch(self, get_date: str = None, **kwargs) -> int:
        """
        주가 목록을 가져오는 함수
        :param get_date: YYYYMMDD
        :param kwargs:
        :return:
        """
        # 1. 값 설정
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

        # 3. 데이터 레이크에 저장
        save_cnt = self._load_to_datalake(res, get_date)

        return save_cnt

    def _load_to_datalake(self, res: requests.Response, get_date: str):
        """
        :param res: 주가 데이터 API 응답 객체
        :param get_date: 주가 데이터 조회 날짜 (YYYYMMDD)
        :return:
        """
        # 1. 결과를 DataFrame으로 변환
        data = pd.DataFrame(res.json()["OutBlock_1"])

        # 2. 데이터 레이크에 저장
        DataLake.save_to_datalake(
            data=data,
            endpoint=EndPoint.STOCK_PRICE,
            source=DataSource.KRX,
            date=get_date,
        )

        return len(data)

    def transform(self, get_date: str, data: pd.DataFrame = None, **kwargs):
        """
        주가 데이터를 처리하는 함수
        :param get_date: 주가 데이터 조회 날짜 (YYYYMMDD)
        :param data:
        :param kwargs:
        :return:
        """
        # 1. 데이터가 없으면 데이터 레이크에서 로드
        data = DataLake.load_from_datalake(
            endpoint=EndPoint.STOCK_PRICE, source=DataSource.KRX, date=get_date
        )

        # 2. 데이터 추가
        data["ucode"] = data.apply(
            lambda x: preprocessing.create_ucode("KR", x["ISU_SRT_CD"]), axis=1
        )
        data["date"] = pd.to_datetime(get_date, format="%Y%m%d").date()

        # 3. 컬럼명 변경
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
        cols = ["mkt_cap", "price", "volume", "list_shrs"]
        for col in cols:
            data[col] = data[col].str.replace(",", "")
        data = data[["ucode", "date", "mkt_cap", "price", "volume", "list_shrs"]]

        # 4. DW 저장
        save_cnt = self._load_to_db(data=data)
        return save_cnt

    def load(self, data: pd.DataFrame, **kwargs):
        """
        주가 데이터를 데이터베이스에 저장하는 함수
        :param data:
        :return:
        """
        uniq = ["ucode", "date"]
        res = self.db.upserts(FactStockPrice, data, uniq)
        return res