from sqlalchemy import Column, String, ForeignKey, DECIMAL, DATE
from sqlalchemy.orm import relationship
from models.warehouse.group.timestamp import Timestamp

class StockPrice(Timestamp):
    uniq_code = Column(String(100), ForeignKey('stocks_base.uniq_code'), primary_key=True, doc="유니크하게 만든 코드")
    value = Column(DECIMAL(precision=10, scale=2), nullable=False)
    date =  Column(DATE, nullable=False)

    # StocksBase 모델과의 관계를 설정합니다.
    stocks_base = relationship("StocksBase", back_populates="StockPrice")
    __tablename__ = 'stock_price'