from sqlalchemy import Column, String, Numeric, Date, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from ...base import Base
from ..group.timestamp import TimestampMixin

# 손익계산서 Profit and Loss Statement
class FactStockPL(Base, TimestampMixin):
    __tablename__ = 'fact_stock_pl'

    ucode = Column(String, ForeignKey('dim_company.ucode'))
    date = Column(Date, nullable=False) # 년월일
    revenue = Column(Numeric(21, 3), nullable=True)  # 매출액
    operating_income_loss = Column(Numeric(21, 3), nullable=True)  # 영업이익
    profit_loss = Column(Numeric(21, 3), nullable=True)  # 순이익

    company = relationship("CompanyDimension", back_populates="fact_stock_pl")


    __table_args__ = (
        PrimaryKeyConstraint('ucode', 'date', name='pk_fact_stock_pl_date_ucode'),
    )