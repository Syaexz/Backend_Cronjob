
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class TaskCreate(BaseModel):
    name: str
    description: Optional[str] = None
    action: str
    frequency: str = "Daily"
    schedule: str
    status: str = "ACTIVE"
    telegram_notify: bool = True


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    action: Optional[str] = None
    frequency: Optional[str] = None
    schedule: Optional[str] = None
    status: Optional[str] = None
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
