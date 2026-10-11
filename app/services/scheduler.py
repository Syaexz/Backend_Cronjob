
import asyncio
from datetime import datetime

from ..database import SessionLocal
from ..models import Task
from .queue import enqueue_task


async def scheduler_loop():
    print("[SCHEDULER] Scheduler dimulai...")

    # Mencegah task masuk antrean berulang pada menit yang sama.
    scheduled_this_minute = set()

    while True:
        db = None

        try:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            current_date = now.strftime("%Y-%m-%d")
            current_minute = now.strftime("%Y-%m-%d %H:%M")
            current_day = now.strftime("%a").upper()[:3]
            current_day_of_month = now.day

            # Hanya menyimpan penanda untuk menit saat ini.
            scheduled_this_minute = {
                item for item in scheduled_this_minute
                if item[0] == current_minute
            }

            db = SessionLocal()
            tasks = (
                db.query(Task)
                .filter(Task.status == "ACTIVE")
                .all()
            )

            for task in tasks:
                # Jam harus cocok.
                if task.schedule != current_time:
                    continue

                # Jika tanggal mulai diisi, jangan jalankan
                # sebelum tanggal tersebut.
                if task.schedule_date and current_date < task.schedule_date:
                    continue

                frequency = (task.frequency or "Daily").lower()
                should_run = False

                if frequency == "once":
                    # Once hanya boleh dijalankan satu kali.
                    should_run = task.last_run is None

                    if task.schedule_date:
                        should_run = (
                            should_run
                            and current_date == task.schedule_date
                        )

                elif frequency == "daily":
                    # Daily berjalan paling banyak sekali sehari.
                    should_run = (
                        task.last_run is None
                        or task.last_run.strftime("%Y-%m-%d") != current_date
                    )

                elif frequency == "weekly":
                    repeat_days = [
                        day.strip().upper()
                        for day in (task.repeat_days or "").split(",")
                        if day.strip()
                    ]

                    should_run = (
                        current_day in repeat_days
                        and (
                            task.last_run is None
                            or task.last_run.strftime("%Y-%m-%d") != current_date
                        )
                    )

                elif frequency == "monthly":
                    should_run = (
                        task.repeat_day_of_month == current_day_of_month
                        and (
                            task.last_run is None
                            or task.last_run.strftime("%Y-%m-%d") != current_date
                        )
                    )

                if not should_run:
                    continue

                key = (current_minute, task.id)

                if key in scheduled_this_minute:
                    continue

                scheduled_this_minute.add(key)
                await enqueue_task(task.id)

                print(
                    f"[SCHEDULER] Task '{task.name}' "
                    f"(ID {task.id}) masuk antrean."
                )

        except Exception as error:
            print(f"[SCHEDULER] Error: {error}")

        finally:
            if db is not None:
                db.close()

        await asyncio.sleep(5)
