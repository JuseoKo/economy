from sqlalchemy import Column, String, UniqueConstraint, Integer, DATE, BOOLEAN
from models.warehouse.group.timestamp import Timestamp
from models.warehouse.group.name import Name
from sqlalchemy.orm import relationship


class AllDate(Timestamp, Name):
    """
    모든 날짜의 기본 테이블
    """
    date = Column(DATE, nullable=False, primary_key=True, comment="일자")
    quarter = Column(String(2), comment="분기 (1Q/2Q/3Q/4Q")
    weekday = Column(Integer, nullable=False, doc="요일 (0: 월요일 6: 일요일)")
    usa_bus_day = Column(BOOLEAN, nullable=False, doc="미국 공휴일 여부")
    kor_bus_day = Column(BOOLEAN, nullable=False, doc="한국 공휴일 여부")

    __tablename__ = "all_date"
