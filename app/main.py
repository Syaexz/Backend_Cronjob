from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from .models import Task
from .schemas import TaskCreate, TaskUpdate


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CronJob Scheduler API",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "CronJob Scheduler API berjalan"
    }


# =========================
# GET SEMUA TASK
# =========================

@app.get("/api/tasks")
def get_tasks(db: Session = Depends(get_db)):

    tasks = db.query(Task).all()

    return tasks


# =========================
# GET TASK BERDASARKAN ID
# =========================

@app.get("/api/tasks/{task_id}")
def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):

    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task tidak ditemukan"
        )

    return task


# =========================
# TAMBAH TASK
# =========================

@app.post("/api/tasks")
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db)
):

    task = Task(
        name=task_data.name,
        schedule=task_data.schedule,
        action=task_data.action,
        priority=task_data.priority
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

    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task tidak ditemukan"
        )

    if task_data.name is not None:
        task.name = task_data.name

    if task_data.schedule is not None:
        task.schedule = task_data.schedule

    if task_data.action is not None:
        task.action = task_data.action

    if task_data.priority is not None:
        task.priority = task_data.priority

    if task_data.status is not None:
        task.status = task_data.status

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

    task = db.query(Task).filter(Task.id == task_id).first()

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