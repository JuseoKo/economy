from pipeline.tasks.stock import krx
import pytest


def test_stock_list_run():
    res = krx.StockList().run("KRX 주식 리스트 수집")


def test_stock_price_run():
    res = krx.StockPrice().run("KRX 주가 목록 수집")

