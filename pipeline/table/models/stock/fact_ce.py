from sqlalchemy import Column, String, Float, Date, ForeignKey, Numeric, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from ...base import Base

# 자본 변동표 Statement of Changes in Equity
class FactStockCE(Base):
    __tablename__ = 'fact_stock_ce'

    ucode = Column(String, ForeignKey('dim_company.ucode'), primary_key=True)
    date = Column(Date, nullable=False) # 년월일
    dividend = Column(Float, nullable=False)  # 배당금
    share_issuance = Column(Numeric(21, 3), nullable=False)  # 자가 주식 발행
    share_redemption = Column(Numeric(21, 3), nullable=False)  # 자가 주식 매입
    treasury_stock_retirement = Column(Numeric(21, 3), nullable=False)  # 자가 주식 소각

    company = relationship("CompanyDimension", back_populates="fact_stock_ce")


    __table_args__ = (
        PrimaryKeyConstraint('ucode', 'date', name='pk_fact_stock_ce_date_ucode'),
    )