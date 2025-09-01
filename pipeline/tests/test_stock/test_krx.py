"""
pipeline.tasks.stock.krx 모듈에 대한 테스트입니다.

이 테스트 파일에는 KRX 데이터 추출, 변환 및 로드 클래스에 대한 단위 테스트가 포함되어 있습니다.
이 테스트는 ETL 프로세스의 각 단계를 독립적으로 검증하도록 설계되었습니다.
"""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from tasks.stock.krx import StockList, StockPrice


# Test data fixtures
@pytest.fixture
def stock_list_data():
    """KRX API에서 반환된 주식 상장 샘플 데이터"""
    return pd.DataFrame(
        {
            "ISU_CD": ["KR7005930003", "KR7000660001"],
            "ISU_NM": ["삼성전자", "SK하이닉스"],
            "ISU_ENG_NM": ["Samsung Electronics", "SK hynix"],
            "MKT_TP_NM": ["KOSPI", "KOSPI"],
            "ISU_SRT_CD": ["005930", "000660"],
        }
    )


@pytest.fixture
def stock_price_data():
    """KRX API에서 반환된 주가 샘플 데이터"""
    return pd.DataFrame(
        {
            "ISU_SRT_CD": ["005930", "000660"],
            "MKTCAP": ["500,000,000,000", "100,000,000,000"],
            "TDD_CLSPRC": ["70,000", "120,000"],
            "ACC_TRDVOL": ["10,000,000", "5,000,000"],
            "LIST_SHRS": ["5,000,000", "1,000,000"],
        }
    )


class TestStockList:
    """StockList class 유닛 테스트 코드"""

    @pytest.mark.unit
    @patch("pipeline.tasks.stock.krx.Request")
    def test_fetch(self, mock_request):
        """fetch 함수가 API를 올바르게 호출하고 DataFrame을 반환하는지 테스트합니다."""
        # 1. Mock 설정
        mock_instance = mock_request.return_value
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "OutBlock_1": [{"ISU_CD": "KR7005930003", "ISU_NM": "삼성전자"}]
        }
        mock_instance.post.return_value = mock_response

        # 2. 함수 실행
        stock_list = StockList()
        result = stock_list.fetch()

        # 3. 테스트 결과 검증
        mock_instance.post.assert_called_once()
        assert isinstance(result, pd.DataFrame)
        assert "ISU_CD" in result.columns

    @pytest.mark.unit
    def test_transform(self, stock_list_data):
        """transform 함수가 데이터를 올바르게 처리하는지 테스트합니다."""
        # 1. 함수 실행
        stock_list = StockList()
        result = stock_list.transform(stock_list_data)

        # 2. 테스트 결과 검증
        assert "ucode" in result.columns
        assert "type" in result.columns
        assert "country" in result.columns
        assert all(result["country"] == "KR")
        assert all(result["type"] == "STOCK")
        assert len(result) == len(stock_list_data)

    @pytest.mark.unit
    @patch("pipeline.tasks.stock.krx.DBConnection")
    def test_load(self, mock_db_connection, stock_list_data):
        """load 함수가 데이터를 데이터베이스에 올바르게 저장하는지 테스트합니다."""
        # 1. Mock 설정
        mock_instance = mock_db_connection.return_value
        mock_instance.upserts.return_value = 2  # 2개 Row가 삽입되었다고 가정

        # 2. 테스트 대상 객체 생성 및 변환
        stock_list = StockList()
        stock_list.db = mock_instance  # DBConnection mock 설정
        transformed_data = stock_list.transform(stock_list_data)

        # 3. 함수 실행
        result = stock_list.load(transformed_data)

        # 3. 테스트 결과 검증
        mock_instance.upserts.assert_called_once()
        assert result == 2


class TestStockPrice:
    """StockPrice class 유닛 테스트 코드"""

    @pytest.mark.unit
    @patch("pipeline.tasks.stock.krx.Request")
    def test_fetch(self, mock_request):
        """fetch 함수가 API를 올바르게 호출하고 DataFrame을 반환하는지 테스트합니다."""
        # 1. Mock 설정
        mock_instance = mock_request.return_value
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "OutBlock_1": [{"ISU_SRT_CD": "005930", "TDD_CLSPRC": "70,000"}]
        }
        mock_instance.post.return_value = mock_response

        # 2. 함수 실행
        stock_price = StockPrice()
        result = stock_price.fetch(get_date="20230101")

        # 3. 테스트 결과 검증
        mock_instance.post.assert_called_once()
        assert isinstance(result, pd.DataFrame)
        assert "ISU_SRT_CD" in result.columns

    @pytest.mark.unit
    def test_transform(self, stock_price_data):
        """transform 함수가 데이터를 올바르게 처리하는지 테스트합니다."""
        # 1. 함수 실행
        stock_price = StockPrice()
        result = stock_price.transform(
            stock_price_data, params={"get_date": "20230101"}
        )

        # 3. 테스트 결과 검증
        assert "ucode" in result.columns
        assert "date" in result.columns
        assert "price" in result.columns
        assert "mkt_cap" in result.columns
        assert result["price"].iloc[0] == "70000"  # Comma removed
        assert len(result) == len(stock_price_data)

    @pytest.mark.unit
    @patch("pipeline.tasks.stock.krx.DBConnection")
    def test_load(self, mock_db_connection, stock_price_data):
        """load 함수가 데이터를 데이터베이스에 올바르게 저장하는지 테스트합니다."""
        # 1. Mock 설정
        mock_instance = mock_db_connection.return_value
        mock_instance.upserts.return_value = 2  # Simulating 2 rows inserted

        # 2. 테스트 대상 객체 생성 및 변환
        stock_price = StockPrice()
        stock_price.db = mock_instance  # DBConnection mock 설정
        transformed_data = stock_price.transform(
            stock_price_data, params={"get_date": "20230101"}
        )

        # 3. 함수 실행
        result = stock_price.load(transformed_data)

        # 3. 테스트 결과 검증
        mock_instance.upserts.assert_called_once()
        assert result == 2
