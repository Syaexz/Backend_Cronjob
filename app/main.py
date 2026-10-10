from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import asyncio

from .database import engine, Base, get_db
from .models import Task
from .schemas import TaskCreate, TaskUpdate
from .services.scheduler import scheduler_loop
from .services.worker import worker_loop
from .models import TaskHistory
from .schemas import TaskHistoryResponse
from typing import List
from sqlalchemy import func
from .services.queue import get_queued_task_ids

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler_task = asyncio.create_task(scheduler_loop())
    worker_task = asyncio.create_task(worker_loop())

    try:
        yield
    finally:
        scheduler_task.cancel()
        worker_task.cancel()

        await asyncio.gather(
            scheduler_task,
            worker_task,
            return_exceptions=True,
        )


app = FastAPI(
    title="CronJob Scheduler API",
    version="1.0.0",
    lifespan=lifespan,
)

# =========================
# GET ALL TASK
# =========================

@app.get("/api/tasks")
def get_tasks(
    db: Session = Depends(get_db)
):

    tasks = db.query(Task).all()

    return tasks


# =========================
# GET TASK BY ID
# =========================

@app.get("/api/tasks/{task_id}")
def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):

    task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task tidak ditemukan"
        )

    return task


# =========================
# CREATE TASK
# =========================

@app.post("/api/tasks")
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db)
):

    task = Task(
        name=task_data.name,
        description=task_data.description,
        action=task_data.action,
        frequency=task_data.frequency,
        schedule=task_data.schedule,
        status=task_data.status,
        telegram_notify=task_data.telegram_notify
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "message": "Task berhasil ditambahkan",
        "data": task
    }


# =========================
# UPDATE TASK
# =========================

@app.put("/api/tasks/{task_id}")
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db)
):

    task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task tidak ditemukan"
        )

    update_data = task_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return {
        "message": "Task berhasil diperbarui",
        "data": task
    }


# =========================
# DELETE TASK
# =========================

@app.delete("/api/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):

    task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task tidak ditemukan"
        )

    db.delete(task)
    db.commit()

    return {
        "message": "Task berhasil dihapus"
    }


@app.get(
    "/api/history",
    response_model=List[TaskHistoryResponse]
)
def get_task_history(
    db: Session = Depends(get_db)
):
    return (
        db.query(TaskHistory)
        .order_by(TaskHistory.id.desc())
        .all()
    )


@app.get("/api/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_tasks = db.query(Task).count()

    active_tasks = (
        db.query(Task)
        .filter(Task.status == "ACTIVE")
        .count()
    )

    total_executions = db.query(TaskHistory).count()

    successful_executions = (
        db.query(TaskHistory)
        .filter(TaskHistory.status == "SUCCESS")
        .count()
    )

    failed_executions = (
        db.query(TaskHistory)
        .filter(TaskHistory.status == "FAILED")
        .count()
    )

    return {
        "total_tasks": total_tasks,
        "active_tasks": active_tasks,
        "total_executions": total_executions,
        "successful_executions": successful_executions,
        "failed_executions": failed_executions
    }

@app.get("/api/logs")
def get_logs(db: Session = Depends(get_db)):
    histories = (
        db.query(TaskHistory)
        .order_by(TaskHistory.id.desc())
        .all()
    )

    return [
        {
            "id": history.id,
            "task_id": history.task_id,
            "task_name": history.task_name,
            "status": history.status,
            "timestamp": history.started_at,
            "output": history.output,
            "error": history.error,
        }
        for history in histories
    ]


@app.get("/api/queue")
def get_queue(db: Session = Depends(get_db)):
    queued_ids = get_queued_task_ids()

    queued_tasks = (
        db.query(Task)
        .filter(Task.id.in_(queued_ids))
        .all()
        if queued_ids
        else []
    )

    return [
        {
            "id": task.id,
            "name": task.name,
            "action": task.action,
            "schedule": task.schedule,
            "status": "QUEUED",
        }
        for task in queued_tasks
    ]
