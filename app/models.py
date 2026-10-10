from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from datetime import datetime

from .database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    description = Column(Text, nullable=True)

    action = Column(String(255), nullable=False)

    frequency = Column(String(50), default="Daily")

    schedule = Column(String(10), nullable=False)

    status = Column(String(20), default="ACTIVE")

    telegram_notify = Column(Boolean, default=True)

    last_run = Column(DateTime, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.now
    )

    
class TaskHistory(Base):
    __tablename__ = "task_history"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, nullable=False, index=True)
    task_name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)
    started_at = Column(DateTime, nullable=False)
    finished_at = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)
    output = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
