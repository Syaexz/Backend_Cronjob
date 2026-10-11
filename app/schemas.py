
import re
from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field, field_validator


class TaskCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    action: str = Field(min_length=1, max_length=255)

    frequency: Literal["Once", "Daily", "Weekly", "Monthly"] = "Daily"
    schedule: str
    schedule_date: Optional[str] = None
    repeat_days: Optional[list[str]] = None
    repeat_day_of_month: Optional[int] = None

    status: Literal["ACTIVE", "PAUSED"] = "ACTIVE"
    telegram_notify: bool = True


class TaskUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None
    action: Optional[str] = Field(default=None, min_length=1, max_length=255)

    frequency: Optional[Literal["Once", "Daily", "Weekly", "Monthly"]] = None
    schedule: Optional[str] = None
    schedule_date: Optional[str] = None
    repeat_days: Optional[list[str]] = None
    repeat_day_of_month: Optional[int] = None

    status: Optional[Literal["ACTIVE", "PAUSED"]] = None
    telegram_notify: Optional[bool] = None


class TaskHistoryResponse(BaseModel):
    id: int
    task_id: int
    task_name: str
    status: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration: Optional[int] = None
    output: Optional[str] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True
