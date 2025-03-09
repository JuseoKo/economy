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
            "csvxls_isNo": "false"
        }
        self.headers.update({"Content-length": "88"})
        res = self.request.post(url=url, data=payload, headers=self.headers)
        return pd.DataFrame(res.json()['OutBlock_1'])

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Returns: 처리된 상장사 목록
        """
        data['security_type'] = "STOCK"
        data['country'] = "KR"
        data['is_yn'] = 'Y'

        data.rename(
            columns={
                "ISU_CD": "isin",
                "ISU_NM": "kr_name",
                "ISU_ENG_NM": "us_name",
                "MKT_TP_NM": "market",
                "ISU_SRT_CD": "symbol"
            }, inplace=True
        )
        data['ucode'] = data.apply(
            lambda x: preprocessing.create_ucode(x["country"], x['symbol']),
            axis=1
        )
        data = data[['security_type', 'country', 'is_yn', 'isin', 'kr_name', 'us_name', 'market', 'symbol', 'ucode']]
        return data

    def load(self, data: pd.DataFrame):
        """
        Returns: 저장된 상장사 목록
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

    def fetch(self, **kwargs) -> pd.DataFrame:
        """
        Returns: 원본 주가 목록

        Args:
            **kwargs: Airflow를 위한 옵션

        Returns: 원본 상장사 목록
        """
        # 1. 설정
        get_date = kwargs.get('params', {}).get('get_date', "20250221")
        url = f"{self.url}comm/bldAttendant/getJsonData.cmd"
        payload = {
            "bld": "dbms/MDC/STAT/standard/MDCSTAT01501",
            "trdDd": get_date,
            "locale": "ko_KR",
            "mktId": "ALL",
            "share": "1",
            "money": "1",
            "csvxls_isNo": "false"
        }
        self.headers.update({"Content-length": "111"})
        # 2. API 호출
        res = self.request.post(url=url, data=payload, headers=self.headers)
        # 3. 결과 반환
        return pd.DataFrame(res.json()['OutBlock_1'])

    def transform(self, data: pd.DataFrame, **kwargs):
        """
        Returns: 처리된 상장사 목록
        """

        # 1. 데이터 추가
        get_date = kwargs.get('params', {}).get('get_date', "20250221")
        data["ucode"] = data.apply(
            lambda x: preprocessing.create_ucode("KR", x['ISU_CD']),
            axis=1
        )
        data['date'] = get_date

        # 2. 컬럼명 변경
        data.rename(
            columns={
                "MKTCAP": "mkt_cap",
                "TDD_CLSPRC": "price",
                "ACC_TRDVOL": "volume",
                "LIST_SHRS": "list_shrs",
            },
            inplace=True
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
        Returns: 저장된 상장사 목록
        """
        uniq = ["ucode"]
        res = self.db.upserts(FactStockPrice, data, uniq)
        return res

class StockShortBalance(KrxBase):
    """
    KRX의 공매도 잔고 데이터를 가져오는 클래스
    http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC02030301
    """
    def __init__(self):
        super().__init__()

    def fetch(self, **kwargs) -> pd.DataFrame:
        """

        """
        pass

    def transform(self, data: pd.DataFrame, **kwargs):
        """
        Returns: 처리된 상장사 목록
        """
        pass

    def load(self, data: pd.DataFrame):
        """
        Returns: 저장된 상장사 목록
        """
        pass


