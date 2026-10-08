from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from .database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    schedule = Column(String, nullable=False)

    action = Column(String, nullable=False)

    priority = Column(String, default="Medium")

    status = Column(String, default="Menunggu")

    created_at = Column(
        DateTime,
        default=datetime.now
    )