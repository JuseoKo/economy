from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import declared_attr


class TimestampMixin:
    @declared_attr
    def created_at(self):
        return Column(DateTime, default=func.now(), nullable=False)

    @declared_attr
    def updated_at(self):
        return Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
