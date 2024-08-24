import FinanceDataReader as fdr
import yfinance as yf
from models.base import DBCrud
from models.warehouse.base.base import AllBase
from models.warehouse.stock.usa_price import UsStockPrice
import pandas as pd
from tasks.utils import preprocessing, utils, default_request
from airflow.logging_config import log

class StockToWarehouse:

    def __init__(self):
        # 1. DB 연결
        self.db = DBCrud(db="api")
        self.session = self.db.create_session()
        self.request = default_request.Request(site="SEC")

    def us_stock_to_base(self):
        """
        나스닥과 뉴옥증시의 목록을 저장하는 함수입니다.
        :return:
        """
        log.info("미국주식 목록 수집")

        # 2. 데이터 크롤링 및 거래소 저장
        url = "https://www.sec.gov/files/company_tickers.json"
        response = self.request.get(url)
        json_data = response.json()

        # 리스트로 변환
        list_data = [{**value} for key, value in json_data.items()]
        df = pd.DataFrame(list_data)
        df.rename(columns={"cik_str": "id", "ticker": "symbol", "title": "full_name"}, inplace=True)
        df['id'] = df['id'].astype(str).str.zfill(10)
        df["type"] = "STOCK"
        df['country'] = "USA"
        df['source'] = "SEC"
        df["uniq_code"] = df.apply(lambda x: preprocessing.uniq_code_prep( "US", x['symbol'], x['type']), axis=1)

        # 4. 저장 StockBase 테이블 'uniq_code', 'id_code', "symbol", "full_name", "type", "country"
        cnt = self.db.pg_bulk_upsert(session=self.db.create_session(), df=df, model=AllBase, uniq_key=["uniq_code"])
        log.info(f"[{cnt}/{len(df)}] 미국주식 목록 완료")
        return cnt

    def us_stock_to_price(self, start_date: str, end_date: str, **kwargs):
        """
        주가 목록을 수집하는 함수입니다.
        Args:
            start_date: YYYY-MM-DD
            end_date: YYYY-MM-DD
            **kwargs: Airflow를 위한 옵션
        Returns:

        """
        start_date = kwargs.get('params', {}).get('start_date', start_date)
        end_date = kwargs.get('params', {}).get('end_date', end_date)

        # 주식 티커를 지정하여 데이터 다운로드
        # 데이터 수집할 티커 목록 리스팅
        symbols = self.session.query(AllBase.symbol, AllBase.uniq_code).filter(AllBase.country == "USA").all()
        symbols = symbols[:1]
        df = pd.DataFrame(columns=["uniq_code", "High", "Low", "Close", "Volume", "Date"])

        cur_cnt = 0
        total_symbols = len(symbols)
        for symbol, uniq in symbols:
            stock = yf.Ticker(symbol)
            data = stock.history(start=start_date, end=end_date)
            data['uniq_code'] = uniq
            data.reset_index(inplace=True)
            df = pd.concat([df, data])
            utils.time_sleep()

            # 로그
            percent_complete = (cur_cnt + 1) / total_symbols * 100
            cur_cnt += 1
            if cur_cnt % 10 == 0:
                log.info(f"[진행률: {percent_complete:.2f}%][수집: {cur_cnt + 1}/{total_symbols}] 미국주식 주가 수집중..")

        # 전처리
        # 필요없는 컬럼 제거
        df = df.drop(columns=["Open", "Dividends", "Stock Splits"])
        # 컬럼 이름변경
        df.rename(columns={"High": "high_p", "Low": "low_p", "Close": "price", "Volume": "volume", "Date": "date"}, inplace=True)
        # 컬럼 변경
        df['date'] = df.apply(lambda x: x['date'].date(), axis=1)
        cnt = self.db.pg_bulk_upsert(session=self.db.create_session(), df=df, model=UsStockPrice, uniq_key=["uniq_code", "date"])
        return cnt

    # def us_stock_to_cik(self):
