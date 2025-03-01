from pipeline.tasks.stock import krx
import pytest

class TestStockList:
    @pytest.mark.integration
    def test_stock_list(self):
        res = self.create_stock_list().run("KRX 주식 리스트 수집")

    @pytest.mark.unit
    def test_stock_list_fetch(self):
        res = self.create_stock_list().fetch()
        print(res)
        assert len(res) > 0

    @pytest.mark.unit
    def test_stock_list_transform(self):
        res = self.create_stock_list().transform()
        assert len(res) > 0

    @pytest.mark.unit
    def test_stock_list_load(self):
        res = self.create_stock_list().load()
        assert len(res) > 0

    @staticmethod
    def create_stock_list():
        return krx.StockList()


class TestStockPrice:

    @pytest.mark.integration
    def test_stock_price(self):
        res = self.create_stock_price().run("KRX 주가 데이터 수집")

    @pytest.mark.unit
    def test_stock_price_fetch(self):
        res = self.create_stock_price().fetch()
        print(res)
        assert len(res) > 0

    @pytest.mark.unit
    def test_stock_list_transform(self):
        res = self.create_stock_price().transform()
        assert len(res) > 0

    @pytest.mark.unit
    def test_stock_list_load(self):
        res = self.create_stock_price().load()
        assert len(res) > 0

    @staticmethod
    def create_stock_price():
        return krx.StockPrice()