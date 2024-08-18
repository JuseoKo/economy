import unittest
from tasks.stock.us_stock import us_stock_to_base

class TestStock(unittest.TestCase):
    def setUp(self):
        pass
    def test_us_stock_base_to_database(self):
        us_stock_to_base()