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
        primary_key=True,
        doc="유니크하게 만든 코드",
    )
    value = Column(DECIMAL(precision=10, scale=2), nullable=False)
    date = Column(DATE, nullable=False)

    # StocksBase 모델과의 관계를 설정합니다.
    base = relationship("AllBase", back_populates="UsStockPrice")
    __tablename__ = "us_stock_price"
    __table_args__ = (UniqueConstraint("uniq_code", "date", name="stock_price_uniq"),)


# 결합 인덱스 설정
Index("idx_stock_price_date_uniq_code", UsStockPrice.uniq_code, UsStockPrice.date)