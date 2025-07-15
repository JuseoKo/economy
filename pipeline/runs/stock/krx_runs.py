from pipeline.tasks.stock import krx


def stock_list_run():
    krx.StockList().run("KRX 주식 리스트 수집")


def stock_price_run():
    krx.StockPrice().run("KRX 주가 목록 수집")

