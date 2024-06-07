from models.warehouse.stock.base import StockBase
from models.base import DBConnection
import requests
import pandas as pd
from airflow.models.variable import Variable


def update_stock_list():
    # 1. 데이터 로드
    session = DBConnection('api').create_session()
    response = requests.get(Variable.get("fmp_stock_list"))

    # 2. 전처리
    df = pd.DataFrame(response.json())
    df.rename(columns={"exchangeShortName": "exchange_symbol", "name": "full_name"}, inplace=True)
    df.drop(columns=['price'], inplace=True)
    df['uniq_code'] = df.apply(lambda x: "UsStock-" + x['symbol'], axis=1)
    df = df[df['exchange_symbol'].isin(['NASDAQ', 'NYSE'])]
    df = df[df['type'].isin(['stock', 'etf', 'etn'])]
    bulk_date = df.to_dict("records")

    # 3. 저장
    session.bulk_insert_mappings(StockBase, bulk_date)
    session.commit()
    session.close()
