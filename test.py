from secedgar import filings, FilingType

# 10Q filings for Apple (ticker "aapl")
my_filings = filings(cik_lookup="aapl",
                     filing_type=FilingType.FILING_10Q,
                     user_agent="test mariat1717@daum.net")
print(my_filings)
my_filings.save('/path/to/dir')
exit()