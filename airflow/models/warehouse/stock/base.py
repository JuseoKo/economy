from sqlalchemy import Column, String, UniqueConstraint, Integer
from models.warehouse.group.timestamp import Timestamp
from models.warehouse.group.name import Name


class StockBase(Timestamp, Name):
    uniq_code = Column(String(100), primary_key=True, comment='내부 관리 코드')
    symbol = Column(String(20), nullable=False, comment='심볼 (MSFT 등)')
    type = Column(String(5), nullable=False, comment='ETF/STOCK/ETN')
    exchange = Column(String(50), nullable=False, comment='거래소')
    industry = Column(String(100), nullable=True, comment='산업')
    industry_code= Column(String(10), nullable=True, comment='산업 코드')

    __tablename__ = "stocks_base"

    # __table_args__ = (
    #     UniqueConstraint("symbol", "exchange_symbol", name="stocks_base_uniq"),
    # )
