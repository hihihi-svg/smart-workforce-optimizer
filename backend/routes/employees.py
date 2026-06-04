from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from data.store import get_current_project

router = APIRouter()

class EmployeeCreate(BaseModel):
    name: str
    skills: List[str]
    experience: int
    workload: int

class EmployeeUpdate(BaseModel):
    skills: List[str]
    experience: int
    workload: int

@router.get("/")
def get_employees():
    return get_current_project()["employees"]

@router.post("/")
def add_employee(emp: EmployeeCreate):
    name_clean = emp.name.strip()
    if not name_clean:
        raise HTTPException(status_code=400, detail="Employee name cannot be empty.")
    
    project = get_current_project()
    # Check duplicate
    for e in project["employees"]:
        if e["name"].lower() == name_clean.lower():
            raise HTTPException(status_code=400, detail=f"Employee '{name_clean}' already exists in this project.")
            
    new_emp = {
        "name": name_clean,
        "skills": [s.strip() for s in emp.skills if s.strip()],
        "experience": emp.experience,
        "workload": emp.workload
    }
    project["employees"].append(new_emp)
    return {"message": f"Employee '{name_clean}' added successfully!", "employee": new_emp}

@router.put("/{name}")
def update_employee(name: str, emp: EmployeeUpdate):
    project = get_current_project()
    for e in project["employees"]:
        if e["name"].lower() == name.lower().strip():
            e["skills"] = [s.strip() for s in emp.skills if s.strip()]
            e["experience"] = emp.experience
            e["workload"] = emp.workload
            return {"message": f"Employee '{e['name']}' updated successfully!", "employee": e}
    raise HTTPException(status_code=404, detail=f"Employee '{name}' not found.")

@router.delete("/{name}")
def delete_employee(name: str):
    project = get_current_project()
    for i, e in enumerate(project["employees"]):
        if e["name"].lower() == name.lower().strip():
            del project["employees"][i]
            return {"message": f"Employee '{name}' deleted successfully!"}
    raise HTTPException(status_code=404, detail=f"Employee '{name}' not found.")
