
import asyncio
import sys
import time
from pathlib import Path
import subprocess


BASE_DIR = Path(__file__).resolve().parents[2]
TASKS_DIR = BASE_DIR / "tasks"


async def execute_task(task):
    script_name = task.action

    # Pastikan hanya nama file Python yang diizinkan
    if (
        Path(script_name).name != script_name
        or not script_name.endswith(".py")
    ):
        return {
            "status": "FAILED",
            "duration": 0,
            "output": "",
            "error": "Nama script tidak valid",
        }

    script_path = TASKS_DIR / script_name

    if not script_path.is_file():
        return {
            "status": "FAILED",
            "duration": 0,
            "output": "",
            "error": f"Script tidak ditemukan: {script_name}",
        }

    start_time = time.perf_counter()

    try:
        result = await asyncio.to_thread(
            subprocess.run,
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(BASE_DIR),
            check=False,
        )

        duration = round(time.perf_counter() - start_time, 2)

        return {
            "status": (
                "SUCCESS" if result.returncode == 0 else "FAILED"
            ),
            "duration": duration,
            "output": result.stdout,
            "error": (
                result.stderr if result.returncode != 0 else ""
            ),
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "FAILED",
            "duration": round(time.perf_counter() - start_time, 2),
            "output": "",
            "error": "Task melebihi batas waktu 60 detik",
        }

    except Exception as error:
        return {
            "status": "FAILED",
            "duration": round(time.perf_counter() - start_time, 2),
            "output": "",
            "error": str(error),
        }
