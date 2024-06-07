import FinanceDataReader as fdr
# nyse = fdr.StockListing('NYSE')
nasdaq = fdr.StockListing('NASDAQ')

ticker_list = " ".join(nasdaq['Symbol'].to_list())
import yfinance as yf
ticker = yf.tickers(ticker_list)
pass