from sqlalchemy import Column, String, Date, ForeignKey, Numeric, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from ...base import Base
from ..group.timestamp import TimestampMixin

# 현금흐름표 Cash Flow Statement
class FactStockCF(Base, TimestampMixin):
    __tablename__ = 'fact_stock_cf'

    # ucode = Column(String, ForeignKey('dim_company.ucode'))
    ucode = Column(String, primary_key=True)
    date = Column(Date, primary_key=True) # 년월일
    date = Column(Date, nullable=False) # 년월일
    beginning_cash_flow = Column(Numeric(21, 3), nullable=True)  # 기초 현금 및 현금성 자산
    end_cash_flow = Column(Numeric(21, 3), nullable=True)  # 기말 현금 및 현금성 자산
    operating_cash_flow = Column(Numeric(21, 3), nullable=True)  # 영업활동현금흐름, 기업 운영으로 인한 현금흐름
    investing_cash_flow = Column(Numeric(21, 3), nullable=True)  # 투자활동현금흐름 추가투자로 인한 현금흐름
    financing_cash_flow = Column(Numeric(21, 3), nullable=True)  # 재무활동 현금흐름
    exchange_rate_cash_flow = Column(Numeric(21, 3), nullable=True)  # 환율변동효과


    # company = relationship("CompanyDimension", back_populates="fact_stock_cf")


    __table_args__ = (
        PrimaryKeyConstraint('ucode', 'date', name='pk_fact_stock_cf_date_ucode'),
    )