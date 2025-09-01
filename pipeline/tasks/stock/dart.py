"""
데이터 소스 http://data.krx.co.kr/contents/MDC/MAIN/main/index.cmd
"""
from typing import Any

from pipeline.table.models.stock.fact_bs import FactStockBS
from pipeline.table.models.stock.fact_cf import FactStockCF
from pipeline.table.models.stock.fact_pl import FactStockPL
from pipeline.table.models.other.dart_report_path import DartReportPath

import time
import pandas as pd
from bs4 import BeautifulSoup
from pipeline.utils.default_request import Request
from pipeline.tasks.common import ELT
from pipeline.table.base import DBConnection
from datetime import datetime
import re
import requests
from pipeline.utils import utils, preprocessing
from airflow.logging_config import log
import io


class DartBase(ELT):
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


class DartPerformanceList(DartBase):
    def __init__(self):
        super().__init__()

    def fetch(self, **kwargs) -> int:
        """
        수집할 재무재표 목록을 가져오는 함수
        """
        # 1. 재무재표 목록 호출
        response = self._get_request()

        # 2. 데이터 레이크에 저장
        self._load_to_datalake(response)
        return 1

    def _get_request(self, **kwargs) -> requests.Response:
        return self.request.post(
            url=self.url + "disclosureinfo/fnltt/dwld/list.do", headers=self.headers
        )

    def _load_to_datalake(self, data: requests.Response) -> None:
        """
        KRX 상장사 목록을 데이터 레이크에 저장
        :param data:
        :return:
        """
        # 1. data lake 저장
        self.DataLake.save_to_datalake(
            data=data.text, endpoint=self.EndPoint.PERFORMANCE_LIST, source=self.DataSource.KRX, data_type="Text"
        )

    def transform(self, **kwargs):
        """
        수집할 재무재표 목록을 추출하는 함수
        """
        # 1. 데이터 레이크 로드
        data = self.DataLake.load_from_datalake(
            endpoint=self.EndPoint.PERFORMANCE_LIST, source=self.DataSource.KRX, data_type="Text"
        )

        # 2. 데이터 전처리
        df = self._preprocessing(data)

        # 3. 데이터 저장
        save_cnt = self._load_to_db(df)
        return save_cnt

    def _preprocessing(self, data:pd.DataFrame, **kwargs) -> pd.DataFrame:
        datas = []

        # 2. 전처리
        # ㄴ 파싱하여 DF 생성
        soup = BeautifulSoup(data, "html.parser")
        for data in soup.find_all("a"):
            if data.get("onclick") is None:
                continue
            parsing_data = re.findall(r"'(.*?)'", data.get("onclick"))
            datas.append(parsing_data)

        # ㄴ 헤더 적재
        df = pd.DataFrame(data=datas, columns=["year", "period", "type", "name"])

        # ㄴ 날짜 문자열 뽑기
        df["file_update_at"] = df["name"].str.split("_").str[-1].str.replace(".zip", "", regex=False)
        # datetime으로 변환
        df["file_update_at"] = pd.to_datetime(df["file_update_at"], format="%Y%m%d%H%M%S")

        return df

    def _load_to_db(self, data: pd.DataFrame, **kwargs):
        uniq = ["year", "period", "type"]
        res = self.db.upserts(DartReportPath, data, uniq)

        return res


class DartPerFormance(DartBase):
    """
    재무재표 데이터를 가져오는 클래스입니다.
    DartPerformanceList 로 목록을 가져와야 정상적으로 실행이 가능합니다.
    """

    def __init__(self):
        super().__init__()

    def fetch(self, get_date: str, **kwargs) -> int:
        """
        필요한 재무재표 목록을 수집하는 함수
        https://opendart.fss.or.kr/cmm/downloadFnlttZip.do?fl_nm=2024_1Q_BS_20250221162310.zip
        """
        # 1. fetch 목록 추출
        fetch_list_df = self._get_fetch_list(get_date=get_date)
        fetch_list_df = fetch_list_df[fetch_list_df["type"] != "CE"]

        # 2. 데이터 수집
        df = self._get_request(fetch_list_df=fetch_list_df)

        # 3. Datalake 저장
        self._load_to_datalake(df)

        return len(df)

    def _get_fetch_list(self, get_date: str, **kwargs) -> pd.DataFrame:
        """
        수집할 데이터 정보를 가져오는 함수입니다.
        :param get_date: YYYYMMDD
        :return:
        """
        target_date = datetime.strptime(get_date, "%Y%m%d").strftime("%Y-%m-%d")
        df = self.db.selects(
            DartReportPath,
            DartReportPath.file_update_at >= target_date
        )
        return df

    def _get_request(self, fetch_list_df: pd.DataFrame, **kwargs) -> pd.DataFrame:

        df = pd.DataFrame()

        for i in range(len(fetch_list_df)):
            # 1. 데이터 수집
            response = self._get_main_data(fetch_list_df, i)

            # 2. zip 파일에서 데이터 추출
            res_list = utils.load_zip_file_to_text(
                io.BytesIO(response.content), "CP949"
            )

            # 3. 데이터 concat
            df = pd.concat([df, self._concat_data(res_list)], axis=0)

        return df

    def _get_main_data(self, get_list: pd.DataFrame, i: int) -> requests.Response:
        params = {"fl_nm": get_list.iloc[i]["name"]}
        url = self.url + "/cmm/downloadFnlttZip.do"
        res = self.request.get(url, params=params, headers=self.headers)
        time.sleep(3)

        return res

    def _load_to_datalake(self, df: pd.DataFrame):
        """
        :param res: 주가 데이터 API 응답 객체
        :param get_date: 주가 데이터 조회 날짜 (YYYYMMDD)
        :return:
        """
        # 1. 데이터 레이크에 저장
        self.DataLake.save_to_datalake(
            data=df,
            endpoint=self.EndPoint.PERFORMANCE,
            source=self.DataSource.KRX
        )

        return len(df)

    @staticmethod
    def _concat_data(res_list: list) -> pd.DataFrame:
        res_df = pd.DataFrame()
        for j in range(len(res_list)):
            # 연결 재무제표만 추출
            if "연결" in res_list[j]["name"]:
                # 텍스트 데이터를 io.StringIO를 이용하여 파일처럼 읽기
                text_io = io.StringIO(res_list[j]["data"])

                # DataFrame 변환 (탭 '\t'을 구분자로 설정)
                df = pd.read_csv(text_io, delimiter="\t", header=None, skiprows=1)
                res_df = pd.concat([res_df, df], axis=0)

        return res_df

    def transform(self, **kwargs) -> int:
        """
        필요한 재무재표 목록을 변환하는 함수

        보고서 타입 : ['1분기보고서', '반기보고서', '3분기보고서', '사업보고서']
        """
        # 1. 데이터 레이크 로드
        df = self.DataLake.load_from_datalake(
            endpoint=self.EndPoint.PERFORMANCE, source=self.DataSource.KRX
        )

        # 2. 데이터 전처리
        res_data = self._preprocessing(df, **kwargs)

        # 3. 데이터 저장
        save_cnt = self._load_to_db(data=res_data, **kwargs)

        return save_cnt

    def _preprocessing(self, df: pd.DataFrame, **kwargs) -> Any:
        # 1. 컬럼명 수정
        re_col = {
            '1': "symbol",
            '7': "date",
            '9': "currency",
            '10': "column",
            '11': "name",
            '12': "value",
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
            "ifrs-full_CashAndCashEquivalents": "cash_and_cash_equivalents",  # 현금및현금성자산
            "ifrs-full_Inventories": "inventory",  # 재고자산
        }

        data = df.rename(columns=re_col)

        # 2. 필요한 컬럼만 선택 및 데이터 전처리
        data = data[list(re_col.values())]
        data = data[data["symbol"] != "[null]"]
        data["symbol"] = data["symbol"].str.replace("[", "").str.replace("]", "")

        # 3. 데이터 피벗
        # 데이터 필터링 (필요한 컬럼만 선택)
        filtered_data = data[
            data["column"].isin(list(target_columns.keys()))
        ].reset_index(drop=True)
        filtered_data = filtered_data.drop_duplicates(
            subset=[item for item in re_col.values() if item != "value"]
        )

        # 특정 컬럼만 피벗
        pivot_data = filtered_data.pivot_table(
            index=[item for item in re_col.values() if item != "value"],
            columns="column",
            values="value",
            aggfunc="first",  # 'firse'가 아니라 'first'가 올바른 표현입니다.
        ).reset_index()
        res_data = (
            pivot_data.groupby(by=["symbol", "date", "currency"]).first().reset_index()
        )

        # 4. 최종 전처리
        res_data["ucode"] = res_data.apply(
            lambda x: preprocessing.create_ucode(
                "KR",
                x["symbol"],
            ),
            axis=1,
        )
        res_data = res_data[res_data["currency"] == "KRW"]
        res_data.drop(columns=["symbol", "currency", "column", "name"], inplace=True)
        res_data.rename(columns=target_columns, inplace=True)
        res_data["date"] = pd.to_datetime(res_data["date"]).dt.date
        res_data = preprocessing.convert_numeric(
            list(target_columns.values()), res_data
        )
        return res_data

    def _load_to_db(self, data: pd.DataFrame, **kwargs) -> int:
        """
        필요한 재무재표 목록을 저장하는 함수
        """
        uniq = ["ucode", "date"]

        # 1. 재무 상태표 저장 (fact_stock_bs)
        bs_cols = [
            "assets",
            "liabilities",
            "current_assets",
            "current_liabilities",
            "cash_and_cash_equivalents",
            "inventory",
        ]
        bs_res = self.db.upserts(FactStockBS, data[uniq + bs_cols], uniq)
        log.info(" 재무 상태표 저장 완료")

        # 2. 현금 흐름표 저장 (fact_stock_cf)
        cf_cols = [
            "beginning_cash_flow",
            "end_cash_flow",
            "operating_cash_flow",
            "investing_cash_flow",
            "financing_cash_flow",
            "exchange_rate_cash_flow",
        ]
        cf_res = self.db.upserts(FactStockCF, data[uniq + cf_cols], uniq)
        log.info(" 현금 흐름표 저장 완료")

        # 3. 손익 계산서 저장 (fact_stock_pl)
        pl_cols = ["revenue", "operating_income_loss", "profit_loss"]
        pl_res = self.db.upserts(FactStockPL, data[uniq + pl_cols], uniq)
        log.info(" 손익 계산서 저장 완료")

        return bs_res + cf_res + pl_res

    def run(self, title: str, **kwargs):
        """
        추출 - 변환 - 저장 실행 함수
        """
        fetch_list_cnt = self._get_fetch_list(**kwargs)
        log.info(f" ✅ [{title}][Row: {len(fetch_list_cnt)}] 수집 데이터 목록 조회 완료")

        fetch_cnt = self.fetch(**kwargs)
        log.info(f" ✅ [{title}][Row: {fetch_cnt}] 데이터 수집 완료 ")

        transform_cnt = self.transform()
        log.info(f" ✅ [{title}][Row: {transform_cnt}] 데이터 변환 완료 ")