from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declared_attr
from models.base import Base


class Timestamp(Base):
    __abstract__ = True

    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=func.now(), nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
