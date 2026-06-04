from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from data.store import get_current_project

router = APIRouter()

class TaskCreate(BaseModel):
    task_id: str
    required_skills: List[str]
    duration: int
    deps: List[str]

class TaskUpdate(BaseModel):
    required_skills: List[str]
    duration: int
    deps: List[str]

@router.get("/")
def get_tasks():
    return get_current_project()["tasks"]

@router.post("/")
def add_task(task: TaskCreate):
    t_id = task.task_id.strip().upper()
    if not t_id:
        raise HTTPException(status_code=400, detail="Task ID cannot be empty.")
    
    project = get_current_project()
    tasks = project["tasks"]
    
    if t_id in tasks:
        raise HTTPException(status_code=400, detail=f"Task ID '{t_id}' already exists.")
    
    # Validate dependencies exist
    for dep in task.deps:
        dep_clean = dep.strip().upper()
        if dep_clean not in tasks:
            raise HTTPException(
                status_code=400, 
                detail=f"Dependency '{dep_clean}' is not a valid task ID."
            )
            
    new_task = {
        "required_skills": [s.strip() for s in task.required_skills if s.strip()],
        "duration": task.duration,
        "deps": [d.strip().upper() for d in task.deps if d.strip()]
    }
    tasks[t_id] = new_task
    return {"message": f"Task '{t_id}' added successfully!", "task_id": t_id, "task": new_task}

@router.put("/{task_id}")
def update_task(task_id: str, task: TaskUpdate):
    t_id = task_id.strip().upper()
    project = get_current_project()
    tasks = project["tasks"]
    
    if t_id not in tasks:
        raise HTTPException(status_code=404, detail=f"Task ID '{t_id}' not found.")
        
    # Validate dependencies exist (cannot depend on self, must exist, cannot form cycle immediately if cycle checker runs on client)
    for dep in task.deps:
        dep_clean = dep.strip().upper()
        if dep_clean == t_id:
            raise HTTPException(status_code=400, detail="A task cannot depend on itself.")
        if dep_clean not in tasks:
            raise HTTPException(
                status_code=400, 
                detail=f"Dependency '{dep_clean}' is not a valid task ID."
            )
            
    tasks[t_id] = {
        "required_skills": [s.strip() for s in task.required_skills if s.strip()],
        "duration": task.duration,
        "deps": [d.strip().upper() for d in task.deps if d.strip()]
    }
    return {"message": f"Task '{t_id}' updated successfully!", "task": tasks[t_id]}

@router.delete("/{task_id}")
def delete_task(task_id: str):
    t_id = task_id.strip().upper()
    project = get_current_project()
    tasks = project["tasks"]
    
    if t_id not in tasks:
        raise HTTPException(status_code=404, detail=f"Task ID '{t_id}' not found.")
        
    # Remove this task from other tasks dependencies
    for tid, task in tasks.items():
        if t_id in task.get("deps", []):
            task["deps"].remove(t_id)
            
    del tasks[t_id]
    return {"message": f"Task '{t_id}' deleted successfully!"}
