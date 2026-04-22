from pydantic import BaseModel

class TaskResponse(BaseModel):
    task_id: str
    status: str