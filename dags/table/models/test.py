# https://docs.python.org/ko/3.12/library/dataclasses.html reference
from dataclasses import dataclass, asdict

from sqlalchemy import Column, Integer, String, create_engine, Text, DateTime, ForeignKey
from ..base import Base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

class BaseModel:
    """
    A base class that provides common methods for ORM models.
    """

    def to_dict(self) -> dict:
        """
        인스턴스에서 dict 생성
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        """
        dict에서 클래스 인스턴스 생성
        """
        return cls(**data)

@dataclass
class Tests(Base, BaseModel):
    """
    CREATE TABLE tests (
    id INTEGER NOT NULL,
    test VARCHAR,
    PRIMARY KEY (id)
);
    """
    __tablename__ = 'tests'

    id = Column(Integer, primary_key=True, index=True)
    test = Column(String)

    def __init__(self, id: int, test: str):
        self.id = id
        self.test = test
