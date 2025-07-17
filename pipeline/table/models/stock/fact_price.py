from sqlalchemy import Column, String, Numeric, Date, BigInteger, UniqueConstraint, PrimaryKeyConstraint
from ...base import Base
from ..group.timestamp import TimestampMixin

# 팩트 테이블 (주가 데이터)
class FactStockPrice(Base, TimestampMixin):
    __tablename__ = 'fact_stock_price'

    # ucode = Column(String, ForeignKey('dim_company.ucode'))
    ucode = Column(String, primary_key=True)
    date = Column(Date, nullable=False) # 년월일
    volume = Column(Numeric(21, 0), nullable=False) # 거래량
    price = Column(Numeric(21, 3), nullable=False) # 주가
    mkt_cap = Column(Numeric(21, 3), nullable=False) # 시가총액
    list_shrs = Column(BigInteger, nullable=False) # 총 주식 수

    # company = relationship("CompanyDimension", back_populates="fact_stock_price")


    __table_args__ = (
        PrimaryKeyConstraint('ucode', name='pk_fact_stock_ucode_date'),
        UniqueConstraint('ucode', 'date', name='uk_fact_stock_ucode_date'),
    )