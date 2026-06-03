from fastapi import APIRouter
from algorithms.trie import Trie
from data.store import employees

router = APIRouter()

@router.get("/skill/{prefix}")
def search_skill(prefix: str):
    # Dynamically build the Trie from the current in-memory employee records
    trie = Trie()
    for emp in employees:
        for skill in emp.get("skills", []):
            trie.insert(skill, emp["name"])
            
    # Search the prefix in the Trie to find matched names
    matched_names = trie.search_prefix(prefix)
    
    # Map matched names back to their full employee records
    matched_employees = []
    for name in matched_names:
        for emp in employees:
            if emp["name"] == name:
                matched_employees.append(emp)
                break
                
    return {
        "skill": prefix,
        "employees": matched_employees
    }
