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

@router.post("/synthesize")
def synthesize_data():
    project = get_current_project()
    
    first_names = [
        "Aarav", "Aditi", "Amit", "Ananya", "Arjun", "Neha", "Rahul", "Priya", "Rohan", "Sneha",
        "Vikram", "Divya", "Sanjay", "Kiran", "Rajesh", "Suresh", "Mahesh", "Ramesh", "Karan", "Pooja",
        "Deepak", "Jyoti", "Abhishek", "Ritu", "Alok", "Shalini", "Sunil", "Preeti", "Vijay", "Anjali"
    ]
    last_names = [
        "Sharma", "Verma", "Gupta", "Kumar", "Singh", "Patel", "Reddy", "Nair", "Joshi", "Rao",
        "Mehra", "Sen", "Roy", "Das", "Choudhury"
    ]
    skills_frontend = ["React", "TypeScript", "HTML", "CSS", "UI/UX", "Figma"]
    skills_backend = ["Java", "Spring Boot", "Node", "Python", "SQL", "C++"]
    skills_devops = ["DevOps", "AWS", "Docker", "Kubernetes", "Linux"]
    skills_ai = ["Python", "ML", "Data Science", "PyTorch", "SQL"]
    skills_qa = ["QA", "Selenium", "Testing"]
    
    all_skill_pools = [skills_frontend, skills_backend, skills_devops, skills_ai, skills_qa]
    all_skills = list(set(skills_frontend + skills_backend + skills_devops + skills_ai + skills_qa))
    
    # Generate 100 employees
    employee_names = set()
    random.seed(42)
    while len(employee_names) < 100:
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        employee_names.add(f"{fn} {ln}")
    employee_names = sorted(list(employee_names))
    
    employees_list = []
    for name in employee_names:
        pool = random.choice(all_skill_pools)
        num_skills = random.randint(2, 4)
        skills = list(set(random.sample(pool, min(num_skills, len(pool)))))
        experience = random.randint(1, 15)
        workload = random.randint(0, 80)
        employees_list.append({
            "name": name,
            "skills": skills,
            "experience": experience,
            "workload": workload
        })
        
    # Generate 20 tasks
    tasks_dict = {}
    for i in range(1, 21):
        task_id = f"T{i}"
        duration = random.randint(2, 7)
        num_req_skills = random.randint(1, 3)
        required_skills = list(set(random.sample(all_skills, min(num_req_skills, len(all_skills)))))
        
        deps = []
        if i > 1:
            num_deps = random.choices([0, 1, 2], weights=[0.4, 0.4, 0.2])[0]
            if num_deps > 0:
                potential_deps = [f"T{j}" for j in range(1, i)]
                deps = sorted(list(set(random.sample(potential_deps, min(num_deps, len(potential_deps))))))
                
        tasks_dict[task_id] = {
            "required_skills": required_skills,
            "duration": duration,
            "deps": deps
        }
        
    project["employees"] = employees_list
    project["tasks"] = tasks_dict
    project["results"] = None # Reset results
    
    return {
        "message": f"Successfully synthesized 100 employees and 20 tasks for active project '{project['name']}'!",
        "employees_count": len(employees_list),
        "tasks_count": len(tasks_dict)
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
