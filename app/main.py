from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from .models import Task

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CronJob Scheduler API"
)


@app.get("/")
def root():
    return {
        "message": "CronJob Scheduler API berjalan"
    }


@app.get("/api/tasks")
def get_tasks(db: Session = Depends(get_db)):

    tasks = db.query(Task).all()

    return tasks


@app.post("/api/tasks")
def create_task(
    name: str,
    schedule: str,
    action: str,
    priority: str = "Medium",
    db: Session = Depends(get_db)
):

    task = Task(
        name=name,
        schedule=schedule,
        action=action,
        priority=priority
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task