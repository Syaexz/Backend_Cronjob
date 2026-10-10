
import asyncio

# Antrean task yang menunggu diproses worker
task_queue = asyncio.Queue()


async def enqueue_task(task_id: int):
    await task_queue.put(task_id)
    print(f"[QUEUE] Task ID {task_id} masuk antrean")


def get_queued_task_ids():
    return list(task_queue._queue)
