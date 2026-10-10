
import asyncio
from datetime import datetime
from ..database import SessionLocal
from ..models import Task, TaskHistory
from .queue import task_queue
from .worker_executor import execute_task


async def worker_loop():
    print("[WORKER] Worker dimulai...")

    while True:
        task_id = await task_queue.get()
        db = SessionLocal()

        try:
            task = db.query(Task).filter(Task.id == task_id).first()

            if not task or task.status != "ACTIVE":
                continue

            task.status = "RUNNING"
            db.commit()

            started_at = datetime.now()
            result = await execute_task(task)

            finished_at = datetime.now()

            history = TaskHistory(
                task_id=task.id,
                task_name=task.name,
                status=result["status"],
                started_at=started_at,
                finished_at=finished_at,
                duration=int(result["duration"] * 1000),
                output=result["output"],
                error=result["error"],
            )

            task.status = (
                "ACTIVE" if result["status"] == "SUCCESS"
                else "ACTIVE"
            )
            task.last_run = finished_at

            db.add(history)
            db.commit()

            print(
                f"[WORKER] {task.name}: {result['status']}"
            )

        except Exception as error:
            db.rollback()
            print(f"[WORKER] Error: {error}")

        finally:
            db.close()
            task_queue.task_done()
