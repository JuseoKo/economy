import unittest
from tasks.stock.us_stock import StockToWarehouse

class TestStock(unittest.TestCase):
    def setUp(self):
        self.run = StockToWarehouse()
        pass
    def test_us_stock_to_base(self):
        cnt = self.run.us_stock_to_base()
        assert cnt > 0

    def test_us_stock_to_price(self):
        cnt = self.run.us_stock_to_price(start_date='2024-01-01', end_date='2024-05-01')
        assert cnt > 0

    def test_us_cik_to_base(self):
        cnt = self.run.us_stock_to_cik()
        assert cnt > 0