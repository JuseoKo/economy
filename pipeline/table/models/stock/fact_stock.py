from sqlalchemy import Column, String, Float, Date, ForeignKey, BigInteger, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from ...base import Base

# 팩트 테이블 (주가 데이터)
class FactStock(Base):
    __tablename__ = 'fact_stock'

    ucode = Column(String, ForeignKey('dim_company.ucode'), primary_key=True)
    date = Column(Date, nullable=False) # 년월일
    volume = Column(BigInteger, nullable=False) # 거래량
    price = Column(Float, nullable=False) # 주가
    mkt_cap = Column(Float, nullable=False) # 시가총액
    list_shrs = Column(BigInteger, nullable=False) # 총 주식 수

    company = relationship("CompanyDimension", back_populates="fact_stock")


    __table_args__ = (
        PrimaryKeyConstraint('ucode', 'date', name='pk_fact_stock_ucode_date'),
    )