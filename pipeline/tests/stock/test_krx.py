from pipeline.tasks.stock import krx
import pytest

@pytest.fixture
def create_cls():
    return krx.StockList()


class TestStockList:

    @pytest.mark.integration
    def test_stock_list(self, create_cls):
        res = create_cls.run()
        assert len(res) > 0

    @pytest.mark.unit
    def test_stock_list_fetch(self, create_cls):
        res = create_cls.fetch()
        assert len(res) > 0

    @pytest.mark.unit
    def test_stock_list_transform(self, create_cls):
        res = create_cls.transform()
        assert len(res) > 0

    @pytest.mark.unit
    def test_stock_list_load(self, create_cls):
        res = create_cls.load()
        assert len(res) > 0
