from sqlalchemy import Column, String, UniqueConstraint, Integer
from models.warehouse.group.timestamp import Timestamp
from models.warehouse.group.name import Name


class AllBase(Timestamp, Name):
    """
    모든 지수의 베이스 테이블
    """
    uniq_code = Column(String(100), primary_key=True, comment='내부 관리 코드')
    symbol = Column(String(20), nullable=False, comment='심볼 (MSFT 등)')
    type = Column(String(5), nullable=False, comment='ETF/STOCK/ETN/INDEX')
    country = Column(String(5), nullable=False, comment='국가코드, USA/KOR ...')
    exchange = Column(String(50), nullable=True, comment='거래소')
    industry = Column(String(100), nullable=True, comment='산업')
    industry_code= Column(String(10), nullable=True, comment='산업 코드')

    __tablename__ = "all_base"

    # __table_args__ = (
    #     UniqueConstraint("symbol", "exchange_symbol", name="stocks_base_uniq"),
    # )
