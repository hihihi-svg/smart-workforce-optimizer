from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from data.store import tasks

router = APIRouter()

class TaskCreate(BaseModel):
    task_id: str
    required_skills: List[str]
    duration: int
    deps: List[str]

@router.get("/")
def get_tasks():
    return tasks

@router.post("/")
def add_task(task: TaskCreate):
    t_id = task.task_id.strip()
    if not t_id:
        raise HTTPException(status_code=400, detail="Task ID cannot be empty.")
    if t_id in tasks:
        raise HTTPException(status_code=400, detail=f"Task ID '{t_id}' already exists.")
    
    # Validate dependencies exist
    for dep in task.deps:
        dep_clean = dep.strip()
        if dep_clean not in tasks:
            raise HTTPException(
                status_code=400, 
                detail=f"Dependency '{dep_clean}' is not a valid task ID."
            )
            
    new_task = {
        "required_skills": [s.strip() for s in task.required_skills if s.strip()],
        "duration": task.duration,
        "deps": [d.strip() for d in task.deps if d.strip()]
    }
    tasks[t_id] = new_task
    return {"message": f"Task '{t_id}' added successfully!", "task_id": t_id, "task": new_task}
