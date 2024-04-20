from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    DECIMAL,
    DATE,
    Index,
    UniqueConstraint,
    text,
    BigInteger,
)
from sqlalchemy.orm import relationship
from models.warehouse.group.timestamp import Timestamp
from models.base import Base


class StockPrice(Timestamp):
    uniq_code = Column(
        String(100),
        ForeignKey("stocks_base.uniq_code"),
        primary_key=True,
        doc="유니크하게 만든 코드",
    )
    value = Column(DECIMAL(precision=10, scale=2), nullable=False)
    date = Column(DATE, nullable=False)

    # StocksBase 모델과의 관계를 설정합니다.
    stocks_base = relationship("StocksBase", back_populates="StockPrice")
    __tablename__ = "stock_price"
    __table_args__ = (UniqueConstraint("uniq_code", "date", name="stocks_price_uniq"),)


# 결합 인덱스 설정
Index("idx_stock_price_date_uniq_code", StockPrice.uniq_code, StockPrice.date)


class BInfo(Base):
    id = Column(BigInteger, primary_key=True)
    m_code = Column(String(100))
    b_num = Column(String(100))
    p_num = Column(String(100))
    __tablename__ = "b_info"


class AInfo(Base):
    id = Column(BigInteger, primary_key=True)
    m_code = Column(text)
    b_num = Column(text)
    p_num = Column(text)
    __tablename__ = "a_info"


class AgentInfo(Base):
    id = Column(BigInteger, primary_key=True)
    담당자사번 = Column(text)
    담당자명 = Column(text)
    소속코드 = Column(text)


class TotalPay(Base):
    id = Column(BigInteger, primary_key=True)
    매체코드 = Column(text)
    대상월 = Column(text)
    광고매출 = Column(text)
    사업자번호 = Column(text)
