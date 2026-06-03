from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from data.store import employees

router = APIRouter()

class EmployeeCreate(BaseModel):
    name: str
    skills: List[str]
    experience: int
    workload: int

@router.get("/")
def get_employees():
    return employees

@router.post("/")
def add_employee(emp: EmployeeCreate):
    name_clean = emp.name.strip()
    if not name_clean:
        raise HTTPException(status_code=400, detail="Employee name cannot be empty.")
    
    new_emp = {
        "name": name_clean,
        "skills": [s.strip() for s in emp.skills if s.strip()],
        "experience": emp.experience,
        "workload": emp.workload
    }
    employees.append(new_emp)
    return {"message": f"Employee '{name_clean}' added successfully!", "employee": new_emp}
