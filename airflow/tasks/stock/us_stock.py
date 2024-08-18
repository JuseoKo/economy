import FinanceDataReader as fdr
from models.base import DBConnection
from models.warehouse.base.base import AllBase
import pandas as pd
from tasks.utils import preprocessing
from airflow.logging_config import log

class StockToWarehouse:

    def __init__(self):
        # 1. DB 연결
        self.db = DBConnection(db="api")

    def us_stock_to_base(self):
        """
        나스닥과 뉴옥증시의 목록을 저장하는 함수입니다.
        :return:
        """
        log.info("미국주식 목록 수집")

        # 2. 데이터 크롤링 및 거래소 저장
        nasdaq = fdr.StockListing('NASDAQ')
        nyse = fdr.StockListing('NYSE')
        nasdaq["exchange"] = "NASDAQ"
        nyse["exchange"] = "NYSE"
        df = pd.concat([nasdaq, nyse])

        # 3. 데이터 전처리
        df.rename(columns={"Symbol": "symbol", "Name": "full_name", "IndustryCode": "industry_code", "Industry": "industry"},
                      inplace=True)
        df["type"] = "STOCK"
        df['country'] = "USA"
        df["uniq_code"] = df.apply(lambda x: preprocessing.uniq_code_prep( "US", x['symbol'], x['type']), axis=1)
        df.drop_duplicates(inplace=True)


        # 4. 저장 StockBase 테이블
        cnt = self.db.pg_bulk_upsert(session=self.db.create_session(), df=df, model=AllBase, uniq_key=["uniq_code"])
        log.info(f"[{cnt}/{len(df)}] 미국주식 목록 완료")
        return cnt

    def us_stock_to_price(self):
        """
        주가 목록을 수집하는 함수입니다.
        Returns:
        """
        pass