# from dags.table.base import DBConnection
# from sqlalchemy import text
#
#
# db = DBConnection().sync_db()
# result = db.execute(text("SELECT version()"))
# print(result.fetchone())
#

# import requests
#
# # 요청 URL
# url = "http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
#
# # 요청할 데이터 (Form Data)



from pipeline.tasks.stock.krx import Krx

krx = Krx()
krx.get_stock_list()

"""
F TABLE
주가
- uniq_k
- 년월일
- 거래량
- 주가


D TABLE

회사 정보
- uniq_k
- 이름
- ETF/ETN/주식 여부
- 상장 여부
- 국가
- 산업군
- ISIN키
- 심볼

날짜 정보
- 년월일
- 년
- 월
- 일
- 주
- 분기



"""