from sqlalchemy import Column, String, DateTime, Text, UniqueConstraint

from ...base import Base
from ..group.timestamp import TimestampMixin
from pgvector.sqlalchemy import Vector as PgVector

# pgvector(Optional)
VECTOR_AVAILABLE = True

class FactNewsArticle(TimestampMixin, Base):
    __tablename__ = "fact_news_article"

    # 팩트 테이블 (뉴스 기사)
    # - 고유키: publisher_code + uid(guid 우선, 없으면 link)
    publisher_code = Column(String, primary_key=True)  # 퍼블리셔 코드(예: bbc)
    uid = Column(String, primary_key=True)  # 기사 고유 ID(guid 우선, 없으면 link)

    # 분류/식별 (단순 문자열 보관)
    category = Column(String, nullable=True)  # 수집 시점의 카테고리 슬러그(예: business)

    # 기사 메타 데이터
    guid = Column(String, nullable=True)  # RSS 항목 GUID/ID(있을 경우)
    title = Column(String, nullable=False)  # 기사 제목
    link = Column(String, nullable=False)  # 원문 링크 URL
    summary = Column(Text, nullable=True)  # 요약(서머리)
    content = Column(Text, nullable=True)  # 본문(미수집 시 서머리로 대체 저장 가능)
    authors = Column(Text, nullable=True)  # 작성자 목록(문자열 조인: ", ")
    tags = Column(Text, nullable=True)  # 태그/키워드 목록(문자열 조인: ", ")
    language = Column(String, nullable=True)  # 기사 언어(예: en)
    published_at = Column(DateTime, nullable=True)  # 게시 시각(가능한 경우)

    # 벡터 임베딩(선택)
    # - Sentence Embeddings 저장(예: dim=384)
    # - LLM/검색 확장 용도
    if VECTOR_AVAILABLE:  # pragma: no cover
        embedding = Column(PgVector(dim=384), nullable=True)  # 임베딩 벡터

    __table_args__ = (
        UniqueConstraint(
            "publisher_code", "link", name="uk_fact_news_article_pub_link"  # 같은 퍼블리셔 내 링크 중복 금지
        ),
    )
