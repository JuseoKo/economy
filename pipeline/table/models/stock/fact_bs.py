from sqlalchemy import Column, String, Date, ForeignKey, Numeric, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from ...base import Base

# 재무 상태표 Balance Sheet
class FactStockBS(Base):
    __tablename__ = 'fact_stock_bs'

    ucode = Column(String, ForeignKey('dim_company.ucode'), primary_key=True)
    date = Column(Date, nullable=False) # 년월일
    total_assets = Column(Numeric(21, 3), nullable=False)  # 자산 총계
    total_liabilities = Column(Numeric(21, 3), nullable=False)  # 부채 총계
    current_assets = Column(Numeric(21, 3), nullable=False)  # 유동자산
    current_liabilities = Column(Numeric(21, 3), nullable=False)  # 유동부채
    cash_and_cash_equivalents = Column(Numeric(21, 3), nullable=False)  # 현금성 자산
    inventory = Column(Numeric(21, 3), nullable=False)  # 재고자산

    company = relationship("CompanyDimension", back_populates="fact_stock_bs")


    __table_args__ = (
        PrimaryKeyConstraint('ucode', 'date', name='pk_fact_stock_bs_date_ucode'),
    )