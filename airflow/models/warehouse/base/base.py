from sqlalchemy import Column, String, UniqueConstraint, Integer
from models.warehouse.group.timestamp import Timestamp
from models.warehouse.group.name import Name
from sqlalchemy.orm import relationship


class AllBase(Timestamp, Name):
    """
    모든 지수의 베이스 테이블
    """
    id = Column(String(100), nullable=False, comment="CIK, ISIN 등 식별코드")
    uniq_code = Column(String(100), primary_key=True, comment="내부 관리 코드")
    symbol = Column(String(20), nullable=False, comment="심볼 (MSFT 등)")
    type = Column(String(5), nullable=False, comment="ETF/STOCK/ETN/INDEX")
    country = Column(String(5), nullable=False, comment="국가코드, USA/KOR ...")
    source = Column(String(30), nullable=False, comment="데이터 소스, S&P Global, SEC 등")

    __tablename__ = "all_base"

    us_stock_prices = relationship("UsStockPrice", back_populates="base")
    stock_info = relationship("StockInfo", back_populates="base")

    # __table_args__ = (
    #     UniqueConstraint("symbol", "exchange_symbol", name="stocks_base_uniq"),
    # )
