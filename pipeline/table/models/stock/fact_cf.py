from sqlalchemy import Column, String, Date, ForeignKey, Numeric, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from ...base import Base

# 현금흐름표 Cash Flow Statement
class FactStockCF(Base):
    __tablename__ = 'fact_stock_cf'

    ucode = Column(String, ForeignKey('dim_company.ucode'), primary_key=True)
    date = Column(Date, nullable=False) # 년월일
    operating_cash_flow = Column(Numeric(21, 3), nullable=False)  # 영업활동현금흐름, 기업 운영으로 인한 현금흐름
    cash_flows_from_investing_activities = Column(Numeric(21, 3), nullable=False)  # 투자활동현금흐름 추가투자로 인한 현금흐름
    cash_flows_from_financing_activities = Column(Numeric(21, 3), nullable=True)  # 재무활동 현금흐름
    foreign_exchange_effect = Column(Numeric(21, 3), nullable=False)  # 환율변동효과


    company = relationship("CompanyDimension", back_populates="fact_stock_cf")


    __table_args__ = (
        PrimaryKeyConstraint('ucode', 'date', name='pk_fact_stock_cf_date_ucode'),
    )