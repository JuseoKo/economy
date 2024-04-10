from sqlalchemy import Column, Integer, String
from models.base import Base
# from models.warehouse.group.timestamp import Timestamp

class StocksBase(Base):
    __tablename__ = 'stocks_base'

    symbol = Column(String, primary_key=True)
    company_name = Column(String, nullable=False)

    # You can use Timestamp here if needed
    # timestamp = Column(Timestamp)

    def __repr__(self):
        return f"<stocks_base(symbol='{self.symbol}')>"