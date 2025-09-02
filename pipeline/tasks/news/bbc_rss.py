from datetime import datetime
from typing import Dict, List, Tuple

import pandas as pd
import feedparser

from pipeline.table.base import DBConnection, Base
from pipeline.table.models.news.dim_publisher import NewsPublisherDimension
from pipeline.table.models.news.fact_article import FactNewsArticle
from pipeline.tasks.common import ELT
from pipeline.utils.datalake import DataLake, DataSource, EndPoint


class BBCNewsRSS(ELT):
    """
    BBC RSS 수집/저장기
    - BBC 주요 RSS를 카테고리별로 수집하여 저장
    - 팩트/디멘션 분리, LLM 확장 대비 벡터 컬럼 지원
    """

    PUBLISHER = {
        "publisher_code": "bbc",
        "name": "BBC News",
        "base_url": "https://www.bbc.com",
        "country": "GB",
        "language": "en",
    }

    # BBC 주요 카테고리 RSS 목록
    FEEDS: Dict[str, str] = {
        # Top stories
        "top": "https://feeds.bbci.co.uk/news/rss.xml",
        # Regions
        "uk": "https://feeds.bbci.co.uk/news/uk/rss.xml",
        "world": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "us_and_canada": "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml",
        # Topics
        "business": "https://feeds.bbci.co.uk/news/business/rss.xml",
        "technology": "https://feeds.bbci.co.uk/news/technology/rss.xml",
        "science_and_environment": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
        "entertainment_and_arts": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
        "health": "https://feeds.bbci.co.uk/news/health/rss.xml",
    }

    def __init__(self) -> None:
        super().__init__()
        self.db = DBConnection()

    # ====== Extract ======
    def fetch(self, **kwargs) -> int:
        """
        BBC RSS를 읽어 원본을 데이터레이크에 저장(DataFrame)
        Returns: 적재 건수
        """
        frames: List[pd.DataFrame] = []
        for slug, url in self.FEEDS.items():
            # 1. RSS 파싱
            parsed = feedparser.parse(url)
            rows = []
            for e in parsed.entries:
                published = None
                if getattr(e, "published", None):
                    try:
                        # 2. 날짜 파싱 (published_parsed 우선)
                        if getattr(e, "published_parsed", None):
                            published = datetime(*e.published_parsed[:6])
                        else:
                            published = pd.to_datetime(e.published, errors="coerce")
                    except Exception:
                        published = None

                guid = getattr(e, "id", None) or getattr(e, "guid", None)
                link = getattr(e, "link", None)
                uid = guid or link  # 3. 업서트용 고유키

                authors = None
                if getattr(e, "authors", None):
                    try:
                        authors = ", ".join([a.get("name") for a in e.authors if a.get("name")])
                    except Exception:
                        authors = None

                tags = None
                if getattr(e, "tags", None):
                    try:
                        tags = ", ".join([t.get("term") for t in e.tags if t.get("term")])
                    except Exception:
                        tags = None

                # 4. 행 구성
                rows.append(
                    {
                        "publisher_code": self.PUBLISHER["publisher_code"],
                        "category": slug,
                        "guid": guid,
                        "uid": uid,
                        "title": getattr(e, "title", None),
                        "link": link,
                        "summary": getattr(e, "summary", None),
                        "content": getattr(e, "summary", None),  # RSS 본문 대체
                        "authors": authors,
                        "tags": tags,
                        "language": self.PUBLISHER["language"],
                        "published_at": published,
                    }
                )

            if rows:
                frames.append(pd.DataFrame(rows))  # 카테고리별 누적

        all_df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        if not all_df.empty:
            # 5. 데이터레이크 저장
            DataLake.save_to_datalake(
                data=all_df,
                endpoint=EndPoint.NEWS_RSS,
                source=DataSource.NEWS_BBC,
            )

        return len(all_df)

    # ====== Transform & Load ======
    def transform(self, **kwargs) -> int:
        """
        DataLake의 BBC RSS 원본을 로드하여
        1) 퍼블리셔 디멘션 업서트
        2) 카테고리 디멘션 업서트
        3) 기사 팩트 업서트
        Returns: 저장 건수
        """
        # 테이블이 없다면 생성 (초기 구동 편의)
        Base.metadata.create_all(
            bind=self.db.sync_engine,
            tables=[
                NewsPublisherDimension.__table__,
                FactNewsArticle.__table__,
            ],
            checkfirst=True,
        )
        df: pd.DataFrame = DataLake.load_from_datalake(
            endpoint=EndPoint.NEWS_RSS, source=DataSource.NEWS_BBC
        )
        if df is None or df.empty:
            return 0

        # 1) 디멘션: 퍼블리셔
        pub_df = pd.DataFrame([
            self.PUBLISHER
        ])["publisher_code name base_url country language".split()]
        self.db.upserts(
            NewsPublisherDimension,
            pub_df,
            uniq_list=["publisher_code"],
        )

        # 2) 팩트: 아티클
        fact_cols = [
            "publisher_code",
            "uid",
            "category",
            "guid",
            "title",
            "link",
            "summary",
            "content",
            "authors",
            "tags",
            "language",
            "published_at",
        ]
        fact_df = df[fact_cols].copy()

        # 2-1) 같은 기사(uid)가 여러 카테고리에 존재 → 기사(행) 중복 제거
        #      최신 게시 시각 우선 보존
        fact_df = fact_df.sort_values("published_at", ascending=False)
        fact_df = fact_df.drop_duplicates(subset=["publisher_code", "uid"], keep="first")

        # 3) 업서트 기준: (publisher_code, uid)
        saved = self.db.upserts(
            FactNewsArticle,
            fact_df,
            uniq_list=["publisher_code", "uid"],
        )
        return saved

    def run_all(self) -> Tuple[int, int]:
        """수집부터 적재까지 한 번에 실행"""
        fetch_n = self.fetch()
        save_n = self.transform()
        return fetch_n, save_n
