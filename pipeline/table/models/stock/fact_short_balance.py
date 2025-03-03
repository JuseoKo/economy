from sqlalchemy import Column, String, Float, Date, ForeignKey, BigInteger, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from ...base import Base
from ..group.timestamp import TimestampMixin

# 팩트 테이블 (공매도 잔고)
class FactStockShortBalance(Base, TimestampMixin):
    __tablename__ = 'fact_stock_short_balance'

    ucode = Column(String, ForeignKey('dim_company.ucode'))
    date = Column(Date, nullable=False) # 년월일
    short_volume = Column(BigInteger, nullable=False)  # 공매도 잔고(주식 수)
    short_ratio = Column(Float, nullable=False)  # 공매도 비율 (%)

    company = relationship("CompanyDimension", back_populates="fact_stock_short_balance")


    __table_args__ = (
        PrimaryKeyConstraint('ucode', 'date', name='pk_fact_stock_short_balance_date_ucode'),
    )