from sqlalchemy import Column, String, Float, Date, ForeignKey, Numeric, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from ...base import Base
from ..group.timestamp import TimestampMixin

# 자본 변동표 Statement of Changes in Equity
class FactStockCE(Base, TimestampMixin):
    __tablename__ = 'fact_stock_ce'

    # ucode = Column(String, ForeignKey('dim_company.ucode'))
    ucode = Column(String, primary_key=True)
    date = Column(Date, primary_key=True) # 년월일
    dividend = Column(Float, nullable=False)  # 배당금
    share_issuance = Column(Numeric(21, 3), nullable=False)  # 자가 주식 발행
    share_redemption = Column(Numeric(21, 3), nullable=False)  # 자가 주식 매입
    treasury_stock_retirement = Column(Numeric(21, 3), nullable=False)  # 자가 주식 소각

    # company = relationship("CompanyDimension", back_populates="fact_stock_ce")


    __table_args__ = (
        PrimaryKeyConstraint('ucode', 'date', name='pk_fact_stock_ce_date_ucode'),
    )