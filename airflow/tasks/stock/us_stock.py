import FinanceDataReader as fdr
from models.base import DBConnection
from models.warehouse.stock.base import StockBase
import pandas as pd

def us_stock_base_to_database():
    """
    나스닥과 뉴옥증시의 목록을 저장하는 함수입니다.
    :return:
    """
    # 1. DB 연결
    db = DBConnection(db="api")

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
    df["uniq_code"] = df.apply(lambda x: f"US_{x['symbol']}_{x['type']}", axis=1)

    # 4. 저장
    db.pg_bulk_upsert(session=db.create_session(), df=df, model=StockBase, uniq_key=["uniq_code"])
