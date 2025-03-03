from sqlalchemy import Column, String, Numeric, Date, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from ...base import Base
from ..group.timestamp import TimestampMixin

# 손익계산서 Profit and Loss Statement
class FactStockPL(Base, TimestampMixin):
    __tablename__ = 'fact_stock_pl'

    ucode = Column(String, ForeignKey('dim_company.ucode'))
    date = Column(Date, nullable=False) # 년월일
    total_revenue = Column(Numeric(21, 3), nullable=False)  # 매출액
    operating_profit = Column(Numeric(21, 3), nullable=False)  # 영업이익
    net_profit = Column(Numeric(21, 3), nullable=False)  # 순이익

    company = relationship("CompanyDimension", back_populates="fact_stock_pl")


    __table_args__ = (
        PrimaryKeyConstraint('ucode', 'date', name='pk_fact_stock_pl_date_ucode'),
    )