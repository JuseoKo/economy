import unittest
from tasks.stock.us_stock import StockToWarehouse

class TestStock(unittest.TestCase):
    def setUp(self):
        self.run = StockToWarehouse()
        pass
    def test_us_stock_to_base(self):
        cnt = self.run.us_stock_to_base()
        assert cnt > 0
