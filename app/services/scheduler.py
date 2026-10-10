
import asyncio
from datetime import datetime

from ..database import SessionLocal
from ..models import Task
from .queue import enqueue_task


async def scheduler_loop():
    print("[SCHEDULER] Scheduler dimulai...")

    # Mencegah task yang sama masuk antrean berulang
    # pada menit yang sama selama proses masih hidup.
    scheduled_this_minute = set()

    while True:
        db = None

        try:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            current_minute = now.strftime("%Y-%m-%d %H:%M")

            # Bersihkan penanda dari menit sebelumnya.
            scheduled_this_minute = {
                item for item in scheduled_this_minute
                if item[0] == current_minute
            }

            db = SessionLocal()

            tasks = (
                db.query(Task)
                .filter(
                    Task.schedule == current_time,
                    Task.status == "ACTIVE",
                )
                .all()
            )

            for task in tasks:
                key = (current_minute, task.id)

                if key in scheduled_this_minute:
                    continue

                scheduled_this_minute.add(key)
                await enqueue_task(task.id)

        except Exception as error:
            print(f"[SCHEDULER] Error: {error}")

        finally:
            if db is not None:
                db.close()

        await asyncio.sleep(5)
