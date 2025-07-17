from sqlalchemy import Column, String, PrimaryKeyConstraint
from ...base import Base
from ..group.timestamp import TimestampMixin


# 회사 차원 테이블
class DartReportPath(TimestampMixin, Base):
    __tablename__ = "dart_report_path"

    year = Column(String, primary_key=True)
    period = Column(String, primary_key=True)  # 회사 이름
    type = Column(String, primary_key=True)  # 회사 영문 이름
    name = Column(String, nullable=False)  # ETF, ETN, 주식 여부

    __table_args__ = (
        PrimaryKeyConstraint("year", "period", "type", name="pk_dart_report_path"),
    )
