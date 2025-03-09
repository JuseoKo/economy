"""
데이터 소스 http://data.krx.co.kr/contents/MDC/MAIN/main/index.cmd
"""
from table.models.stock.fact_bs import FactStockBS
from table.models.stock.fact_cf import FactStockCF
from table.models.stock.fact_pl import FactStockPL

import time
import pandas as pd
from bs4 import BeautifulSoup
from pipeline.utils.default_request import Request
from pipeline.tasks.common import ETL
from pipeline.table.base import DBConnection
import re
import requests
from pipeline.utils import utils, preprocessing
from airflow.logging_config import log
import io


class DartBase(ETL):
    def __init__(self):
        super().__init__()
        self.request = Request()
        self.db = DBConnection()
        self.url = "https://opendart.fss.or.kr/"
        self.headers = {
            "Accept": "text/html, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
            "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "opendart.fss.or.kr",
            "Origin": "https://opendart.fss.or.kr",
            "Referer": "http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?",
        }


# 재무재표 수집
class DartPerFormance(DartBase):
    """

    """
    def __init__(self):
        super().__init__()

    def fetch_list(self, **kwargs):
        """
        수집할 재무재표 목록을 가져오는 함수
        """
        res = self.request.post(
            url=self.url + "disclosureinfo/fnltt/dwld/list.do",
            headers=self.headers
        )
        return res

    @staticmethod
    def extract(data: requests.Response, **kwargs):
        """
        수집할 재무재표 목록을 추출하는 함수
        """
        datas = []

        # 전처리
        soup = BeautifulSoup(data.text, "html.parser")
        for data in soup.find_all("a"):
            if data.get("onclick") is None:
                continue
            parsing_data = re.findall(r"'(.*?)'", data.get("onclick"))
            datas.append(parsing_data)

        df = pd.DataFrame(data=datas, columns=["year", "period", "type", 'name'])
        return df

    def _get_main_data(self, get_list: pd.DataFrame, i: int) -> requests.Response:
        params = {
            "fl_nm": get_list.iloc[i]['name']
        }
        url = self.url + "/cmm/downloadFnlttZip.do"
        res = self.request.get(url, params=params, headers=self.headers)
        time.sleep(3)

        return res

    @staticmethod
    def _concat_data(res_list: list) -> pd.DataFrame:
        res_df = pd.DataFrame()
        for j in range(len(res_list)):

            # 연결 재무제표만 추출
            if "연결" in res_list[j]['name']:
                # 텍스트 데이터를 io.StringIO를 이용하여 파일처럼 읽기
                text_io = io.StringIO(res_list[j]['data'])

                # DataFrame 변환 (탭 '\t'을 구분자로 설정)
                df = pd.read_csv(text_io, delimiter="\t", header=None, skiprows=1)
                res_df = pd.concat([res_df, df], axis=0)

        return res_df

    def fetch(self, get_list: pd.DataFrame) -> pd.DataFrame|list:
        """
        필요한 재무재표 목록을 수집하는 함수
        https://opendart.fss.or.kr/cmm/downloadFnlttZip.do?fl_nm=2024_1Q_BS_20250221162310.zip

        """
        df = pd.DataFrame()
        get_list = get_list[get_list['type'] != 'CE'][:12]
        for i in range(len(get_list)):
            # 1. 데이터 수집
            response = self._get_main_data(get_list, i)

            # 2. zip 파일에서 데이터 추출
            res_list = utils.load_zip_file_to_text(io.BytesIO(response.content), "CP949")

            # 3. 데이터 concat
            df = pd.concat([df, self._concat_data(res_list)], axis=0)

        return df


    def transform(self, data: pd.DataFrame, **kwargs):
        """
        필요한 재무재표 목록을 변환하는 함수

        보고서 타입 : ['1분기보고서', '반기보고서', '3분기보고서', '사업보고서']
        """
        # 1. 컬럼명 수정
        re_col = {
                1: "symbol",
                7: "date",
                9: "currency",
                10: "column",
                11: "name",
                12: "value"
            }

        # 피벗할 특정 컬럼 리스트
        target_columns = {
            "ifrs-full_Revenue": "revenue",  # 매출액
            "ifrs-full_ProfitLoss": "profit_loss",  # 순이익
            "dart_OperatingIncomeLoss": "operating_income_loss",  # 영업이익
            "dart_CashAndCashEquivalentsAtBeginningOfPeriodCf": "beginning_cash_flow",  # 기초 현금 및 현금성자산
            "dart_CashAndCashEquivalentsAtEndOfPeriodCf": "end_cash_flow",  # 기말 현금 및 현금성 자산
            "ifrs-full_CashFlowsFromUsedInFinancingActivities": "financing_cash_flow",  # 재무활동현금흐름
            "ifrs-full_CashFlowsFromUsedInInvestingActivities": "investing_cash_flow",  # 투자활동현금흐름
            "ifrs-full_CashFlowsFromUsedInOperatingActivities": "operating_cash_flow",  # 영업활동현금흐름
            "ifrs-full_EffectOfExchangeRateChangesOnCashAndCashEquivalents": "exchange_rate_cash_flow",  # 환율효과에 의한 변화량
            "ifrs-full_Assets": "assets",  # 자산총계
            "ifrs-full_Liabilities": "liabilities",  # 부채총계
            "ifrs-full_CurrentAssets": "current_assets",  # 유동자산
            "ifrs-full_CurrentLiabilities": "current_liabilities",  # 유동부채
            "ifrs-full_CashAndCashEquivalents": "cash_and_cash_equivalents", # 현금및현금성자산
            "ifrs-full_Inventories": "inventory",  # 재고자산
        }

        data = data.rename(
            columns=re_col
        )
        # 2. 필요한 컬럼만 선택 및 데이터 전처리
        data = data[list(re_col.values())]
        data = data[data['symbol'] != '[null]']
        data['symbol'] = data['symbol'].str.replace('[', '').str.replace(']', '')

        # 3. 데이터 피벗

        # 데이터 필터링 (필요한 컬럼만 선택)
        filtered_data = data[data["column"].isin(list(target_columns.keys()))].reset_index(drop=True)
        filtered_data = filtered_data.drop_duplicates(subset=[item for item in re_col.values() if item != 'value'])

        # 특정 컬럼만 피벗
        pivot_data = filtered_data.pivot_table(
            index=[item for item in re_col.values() if item != 'value'],
            columns="column",
            values="value",
            aggfunc='first'  # 'firse'가 아니라 'first'가 올바른 표현입니다.
        ).reset_index()
        res_data = pivot_data.groupby(by=['symbol', 'date', 'currency']).first().reset_index()

        # 4. 최종 전처리
        res_data['ucode'] = res_data.apply(lambda x: preprocessing.create_ucode("KR", x['symbol'], ), axis=1)
        res_data = res_data[res_data['currency'] == 'KRW']
        res_data.drop(columns=['symbol', 'currency', 'column', 'name'], inplace=True)
        res_data.rename(columns=target_columns, inplace=True)
        res_data = preprocessing.convert_numeric(list(target_columns.values()), res_data)

        return res_data


    def load(self, data: pd.DataFrame):
        """
        필요한 재무재표 목록을 저장하는 함수
        """
        uniq = ["ucode", "date"]


        # 1. 재무 상태표 저장 (fact_stock_bs)
        bs_col = ["assets", "liabilities", "current_assets", "current_liabilities", "cash_and_cash_equivalents", "inventory"]
        res = self.db.upserts(FactStockBS, data[uniq + bs_col], uniq)
        # 2. 현금 흐름표 저장 (fact_stock_cf)
        res = self.db.upserts(FactStockCF, data, uniq)
        # 3. 손익 개산서 저장 (fact_stock_pl)
        res = self.db.upserts(FactStockPL, data, uniq)

        pass

    def run(self, title: str):
        """
        추출 - 변환 - 저장 실행 함수
        """
        fetch_list = self.fetch_list()
        fetch_list = self.extract(data=fetch_list)

        fetch = self.fetch(data=fetch_list)
        log.info(f" ✅ [{title}][Row: {len(fetch)}] 데이터 수집 완료 ")

        transform = self.transform(data=fetch)
        log.info(f" ✅ [{title}][Row: {len(transform)}/{len(fetch)}] 데이터 변환 완료 ")

        load = self.load(data=transform)
        log.info(f" ✅ [{title}][Row: {load}/{len(transform)}] 데이터 저장 완료 ")