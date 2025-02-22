from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from ...base import Base

# 팩트 테이블 (주가 데이터)
class FactStock(Base):
    __tablename__ = 'fact_stock'

    ucode = Column(String, ForeignKey('dim_company.ucode'), primary_key=True)
    date = Column(Date, nullable=False) # 년월일
    volume = Column(Integer, nullable=False) # 거래량
    stock_price = Column(Float, nullable=False) # 주가

    company = relationship("CompanyDimension", back_populates="fact_records")