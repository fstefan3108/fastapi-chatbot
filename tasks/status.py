import json
from tasks.redis_client import r

def update_task_status(task_id: str, status: str, result: dict | None = None):
    data = {"status": status, "result": result}
    r.set(task_id, json.dumps(data), ex=3600)