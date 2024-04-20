from sqlalchemy import Column, String
from models.base import Base


class Name(Base):
    __abstract__ = True
    full_name = Column(String, nullable=True)
    name = Column(String, nullable=True)
