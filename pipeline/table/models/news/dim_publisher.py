from sqlalchemy import Column, String, UniqueConstraint

from ...base import Base
from ..group.timestamp import TimestampMixin


# 퍼블리셔 차원 테이블
# - 뉴스 제공자 메타데이터 저장
# - 예: bbc, guardian, reuters


class NewsPublisherDimension(TimestampMixin, Base):
    __tablename__ = "dim_news_publisher"

    # 퍼블리셔 식별 코드(예: 'bbc', 'guardian', 'reuters')
    publisher_code = Column(String, primary_key=True)  # 퍼블리셔 고유 코드
    name = Column(String, nullable=False)  # 퍼블리셔 이름(노출용)
    base_url = Column(String, nullable=True)  # 기본 웹사이트 URL
    country = Column(String, nullable=True)  # 국가 코드(ISO-3166, 예: GB, US)
    language = Column(String, nullable=True)  # 언어 코드(ISO-639-1, 예: en, ko)

    __table_args__ = (
        UniqueConstraint("name", name="uk_dim_news_publisher_name"),  # 이름 유니크 보장
    )
