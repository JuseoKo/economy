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


class UsStockPrice(Timestamp):
    uniq_code = Column(
        String(100),
        ForeignKey("all_base.uniq_code"),
        nullable=False,
        doc="유니크하게 만든 코드",
    )
    price = Column(DECIMAL(precision=10, scale=5), nullable=False, doc="주가")
    high_p = Column(DECIMAL(precision=10, scale=5), nullable=False, doc="당일 최고가")
    low_p = Column(DECIMAL(precision=10, scale=5), nullable=False, doc="당일 최저가")
    volume = Column(BigInteger, nullable=False, doc="거래량")
    date = Column(DATE, nullable=False)

    # StocksBase 모델과의 관계를 설정합니다.
    base = relationship("AllBase", back_populates="us_stock_prices")
    __tablename__ = "us_stock_price"
    __table_args__ = (UniqueConstraint("uniq_code", "date", name="stock_price_uniq"),)
    # 기본 키를 지정합니다
    __mapper_args__ = {
        'primary_key': [uniq_code, date]
    }

# 결합 인덱스 설정
Index("idx_stock_price_date_uniq_code", UsStockPrice.uniq_code, UsStockPrice.date)
