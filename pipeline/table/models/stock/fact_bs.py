from sqlalchemy import Column, Date, Numeric, PrimaryKeyConstraint, String

from ...base import Base
from ..group.timestamp import TimestampMixin


# 재무 상태표 Balance Sheet
class FactStockBS(Base, TimestampMixin):
    __tablename__ = "fact_stock_bs"

    # ucode = Column(String, ForeignKey('dim_company.ucode'))
    ucode = Column(String, primary_key=True)
    date = Column(Date, primary_key=True)  # 년월일
    assets = Column(Numeric(21, 0), nullable=True)  # 자산 총계
    liabilities = Column(Numeric(21, 0), nullable=True)  # 부채 총계
    current_assets = Column(Numeric(21, 0), nullable=True)  # 유동자산
    current_liabilities = Column(Numeric(21, 0), nullable=True)  # 유동부채
    cash_and_cash_equivalents = Column(Numeric(21, 0), nullable=True)  # 현금성 자산
    inventory = Column(Numeric(21, 0), nullable=True)  # 재고자산

    # company = relationship("CompanyDimension", back_populates="fact_stock_bs")

    __table_args__ = (
        PrimaryKeyConstraint("ucode", "date", name="pk_fact_stock_bs_date_ucode"),
    )
