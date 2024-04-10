from sqlalchemy import Column, String, UniqueConstraint
from models.warehouse.group.timestamp import Timestamp
from models.warehouse.group.name import Name

class StockBase(Timestamp, Name):
    uniq_code = Column(String(100), primary_key=True)
    symbol = Column(String(20), nullable=False)
    type = Column(String(5), nullable=False)
    exchange = Column(String(50), nullable=True)
    exchange_symbol = Column(String(10), nullable=False)

    __tablename__ = 'stocks_base'

    __table_args__ = (
        UniqueConstraint('symbol', 'exchange_symbol', name='stocks_base_uniq'),
    )