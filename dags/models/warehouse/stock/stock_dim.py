from sqlalchemy import Column, Integer, String
from models.base import Base

class Stock(Base):
    __tablename__ = 'stocks'

    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    company_name = Column(String, nullable=False)

    def __repr__(self):
        return f"<Stock(symbol='{self.symbol}')>"
