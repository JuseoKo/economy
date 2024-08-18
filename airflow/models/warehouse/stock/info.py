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


class StockInfo(Timestamp):
    uniq_code = Column(
        String(100),
        ForeignKey("all_base.uniq_code"),
        primary_key=True,
        doc="유니크하게 만든 코드",
    )
    sector = Column(String(100), nullable=False, doc="종목 섹터")
    public_date = Column(DATE, nullable=False, doc="상장일")
    private_date = Column(DATE, nullable=True, doc="상장 폐지일")


    # StocksBase 모델과의 관계를 설정합니다.
    base = relationship("AllBase", back_populates="stock_info")
    __tablename__ = "stock_info"


# 결합 인덱스 설정
# Index("idx_stock_price_date_uniq_code", StockInfo.uniq_code, StockInfo.date)


