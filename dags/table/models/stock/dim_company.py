from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import relationship
from ...base import Base

# 회사 차원 테이블
class CompanyDimension(Base):
    __tablename__ = 'dim_company'
    ucode = Column(String, primary_key=True)
    isin = Column(String, unique=True, nullable=False)
    kr_name = Column(String, nullable=True) # 회사 이름
    us_name = Column(String, nullable=True) # 회사 영문 이름
    security_type = Column(String, nullable=False)  # ETF, ETN, 주식 여부
    is_listed = Column(String, nullable=False)  # 상장 여부 (예: 'Y' or 'N')
    country = Column(String, nullable=False) # 본사 국가
    industry = Column(String, nullable=True) # 산업
    symbol = Column(String, nullable=False) # 회사 식별 코드

    fact_records = relationship("FactStock", back_populates="company")