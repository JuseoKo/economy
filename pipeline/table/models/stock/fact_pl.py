from sqlalchemy import Column, Date, Numeric, PrimaryKeyConstraint, String

from ...base import Base
from ..group.timestamp import TimestampMixin


# 손익계산서 Profit and Loss Statement
class FactStockPL(Base, TimestampMixin):
    __tablename__ = "fact_stock_pl"

    # ucode = Column(String, ForeignKey('dim_company.ucode'))
    ucode = Column(String, primary_key=True)
    date = Column(Date, primary_key=True)  # 년월일
    revenue = Column(Numeric(21, 0), nullable=True)  # 매출액
    operating_income_loss = Column(Numeric(21, 0), nullable=True)  # 영업이익
    profit_loss = Column(Numeric(21, 0), nullable=True)  # 순이익

    # company = relationship("CompanyDimension", back_populates="fact_stock_pl")

    __table_args__ = (
        PrimaryKeyConstraint("ucode", "date", name="pk_fact_stock_pl_date_ucode"),
    )
