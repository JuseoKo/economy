from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import relationship
from ...base import Base

# 회사 차원 테이블
class CompanyDimension(Base):
    __tablename__ = 'dim_company'

    ucode = Column(String, primary_key=True)
    kr_name = Column(String, nullable=True) # 회사 이름
    us_name = Column(String, nullable=True) # 회사 영문 이름
    security_type = Column(String, nullable=False)  # ETF, ETN, 주식 여부
    market = Column(String, nullable=False) # 상장 거래소
    symbol = Column(String, nullable=False) # 회사 식별 코드
    country = Column(String, nullable=False) # 국가
    isin = Column(String, nullable=False)
    is_yn = Column(String, nullable=False)  # 상장 여부 (예: 'Y' or 'N')

    fact_stock = relationship("FactStockPrice", back_populates="company")
    fact_stock_short_balance = relationship("FactStockShortBalance", back_populates="company")
    fact_stock_short_seller = relationship("FactStockShortSeller", back_populates="company")