from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import random
from data.store import (
    projects, get_current_project, set_current_project, 
    create_project, duplicate_project, delete_project
)

router = APIRouter()

class ProjectCreate(BaseModel):
    id: str
    name: str
    description: str

class ProjectDuplicate(BaseModel):
    new_id: str
    new_name: str

class SettingsUpdate(BaseModel):
    top_k: int
    weights: Dict[str, float]
    max_workload: int
    min_experience: int
    availability_filter: bool
    run_greedy: bool
    run_hungarian: bool
    run_bb: bool

@router.get("/")
def list_projects():
    # Return brief info of all projects
    summaries = []
    for pid, proj in projects.items():
        summaries.append({
            "id": proj["id"],
            "name": proj["name"],
            "description": proj["description"],
            "employees_count": len(proj["employees"]),
            "tasks_count": len(proj["tasks"]),
            "has_results": proj["results"] is not None
        })
    return summaries

@router.get("/active")
def get_active_project():
    proj = get_current_project()
    return {
        "id": proj["id"],
        "name": proj["name"],
        "description": proj["description"],
        "settings": proj["settings"]
    }

@router.post("/active/{project_id}")
def switch_project(project_id: str):
    if set_current_project(project_id):
        proj = get_current_project()
        return {"message": f"Switched to project '{proj['name']}' successfully!", "project": proj}
    raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")

@router.post("/")
def add_project(proj: ProjectCreate):
    pid = proj.id.strip().lower().replace(" ", "_")
    if not pid:
        raise HTTPException(status_code=400, detail="Project ID cannot be empty.")
    if create_project(pid, proj.name, proj.description):
        return {"message": f"Project '{proj.name}' created successfully!", "project_id": pid}
    raise HTTPException(status_code=400, detail=f"Project ID '{pid}' already exists.")

@router.post("/duplicate/{project_id}")
def duplicate(project_id: str, payload: ProjectDuplicate):
    new_pid = payload.new_id.strip().lower().replace(" ", "_")
    if not new_pid:
        raise HTTPException(status_code=400, detail="New project ID cannot be empty.")
    if duplicate_project(project_id, new_pid, payload.new_name):
        return {"message": f"Project duplicated as '{payload.new_name}'!", "project_id": new_pid}
    raise HTTPException(status_code=400, detail=f"Duplicate failed. Either source does not exist or target ID is already taken.")

@router.delete("/{project_id}")
def remove_project(project_id: str):
    if len(projects) <= 1:
        raise HTTPException(status_code=400, detail="Cannot delete the only remaining project.")
    if delete_project(project_id):
        return {"message": f"Project '{project_id}' deleted successfully!"}
    raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")
class ProjectImport(BaseModel):
    name: str
    description: str
    employees: List[Dict[str, Any]]
    tasks: Dict[str, Dict[str, Any]]

@router.post("/import")
def import_project(payload: ProjectImport):
    name_clean = payload.name.strip()
    if not name_clean:
        raise HTTPException(status_code=400, detail="Project name cannot be empty.")
    
    pid = name_clean.lower().replace(" ", "_")
    pid = "".join([c for c in pid if c.isalnum() or c == "_"])
    if not pid:
        pid = f"imported_project_{random.randint(1000, 9999)}"
        
    if pid in projects:
        pid = f"{pid}_{random.randint(100, 999)}"
        
    # Validation of employees format
    for emp in payload.employees:
        if "name" not in emp or "skills" not in emp:
            raise HTTPException(status_code=400, detail="Each employee must have a 'name' and 'skills' list.")
        if not isinstance(emp["skills"], list):
            raise HTTPException(status_code=400, detail=f"Employee '{emp.get('name')}' skills must be a list of strings.")
        emp["experience"] = int(emp.get("experience", 0))
        emp["workload"] = int(emp.get("workload", 0))
            
    # Validation of tasks format
    for tid, task in payload.tasks.items():
        if "name" not in task:
            task["name"] = f"Task {tid}"
        if "required_skills" not in task:
            task["required_skills"] = []
        if "duration" not in task:
            task["duration"] = 1
        if "deps" not in task:
            task["deps"] = []
            
        if not isinstance(task["required_skills"], list):
            raise HTTPException(status_code=400, detail=f"Task '{tid}' required_skills must be a list of strings.")
        if not isinstance(task["deps"], list):
            raise HTTPException(status_code=400, detail=f"Task '{tid}' deps must be a list of task ID strings.")
            
        task["duration"] = int(task["duration"])
        
        # Check task dependencies exist in payload.tasks keys
        for dep in task["deps"]:
            if dep not in payload.tasks:
                raise HTTPException(status_code=400, detail=f"Task '{tid}' depends on non-existent task '{dep}'.")

    # Create the project entry
    projects[pid] = {
        "id": pid,
        "name": name_clean,
        "description": payload.description or "Imported custom dataset",
        "employees": payload.employees,
        "tasks": payload.tasks,
        "results": None,
        "settings": {
            "top_k": 3,
            "weights": {
                "skill_match": 0.4,
                "experience": 0.3,
                "workload_penalty": 0.2,
                "estimated_time": 0.1
            },
            "max_workload": 80,
            "min_experience": 0,
            "availability_filter": True,
            "run_greedy": True,
            "run_hungarian": True,
            "run_bb": True,
            "bb_max_depth": 50,
            "animation_speed": "Fast"
        }
    }
    
    # Switch to this project
    set_current_project(pid)
    
    return {
        "message": f"Project '{name_clean}' imported successfully!",
        "project_id": pid,
        "employees_count": len(payload.employees),
        "tasks_count": len(payload.tasks)
    }

@router.post("/synthesize")
def synthesize_data():
    project = get_current_project()

    from data.employees import employees as canonical_employees
    from data.tasks import tasks as canonical_tasks
    import copy

    employees_list = [dict(emp) for emp in canonical_employees]
    tasks_dict     = {k: dict(v) for k, v in canonical_tasks.items()}

    project["employees"] = employees_list
    project["tasks"]     = tasks_dict
    project["results"]   = None

    return {
        "message": (
            f"Loaded canonical dataset: {len(employees_list)} employees and "
            f"{len(tasks_dict)} tasks into '{project['name']}'."
        ),
        "employees_count": len(employees_list),
        "tasks_count":     len(tasks_dict)
    }

@router.post("/active/settings")
def update_active_settings(payload: SettingsUpdate):
    project = get_current_project()
    project["settings"] = {
        "top_k": payload.top_k,
        "weights": payload.weights,
        "max_workload": payload.max_workload,
        "min_experience": payload.min_experience,
        "availability_filter": payload.availability_filter,
        "run_greedy": payload.run_greedy,
        "run_hungarian": payload.run_hungarian,
        "run_bb": payload.run_bb
    }
    project["results"] = None # clear cached results when settings change
    return {"message": "Settings updated successfully!", "settings": project["settings"]}

@router.post("/active/reset")
def reset_active_data():
    project = get_current_project()
    if project["id"] == "project_alpha":
        # Reset Project Alpha to initial 100/20 data
        return synthesize_data()
    else:
        # Reset other projects to empty state
        project["employees"] = []
        project["tasks"] = {}
        project["results"] = None
        return {"message": f"Project '{project['name']}' has been reset to empty.", "employees_count": 0, "tasks_count": 0}
