from data.employees import employees as default_employees
from data.tasks import tasks as default_tasks

# Multi-project store dictionary holding dynamic data for self-contained projects
projects = {
    "project_alpha": {
        "id": "project_alpha",
        "name": "Project Alpha (Enterprise)",
        "description": "Large-scale enterprise workforce assignment (100 employees, 20 tasks)",
        "employees": [dict(emp) for emp in default_employees],
        "tasks": {k: dict(v) for k, v in default_tasks.items()},
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
    },
    "project_beta": {
        "id": "project_beta",
        "name": "Project Beta (Standard)",
        "description": "Standard prototyping task assignments",
        "employees": [
            {"name": "Ramesh", "skills": ["Python", "ML"], "experience": 5, "workload": 60},
            {"name": "Suresh", "skills": ["Python"], "experience": 2, "workload": 20},
            {"name": "Mahesh", "skills": ["Python", "ML"], "experience": 6, "workload": 30},
            {"name": "Kiran", "skills": ["ML"], "experience": 4, "workload": 10}
        ],
        "tasks": {
            "T1": {"required_skills": ["Python", "ML"], "duration": 2, "deps": []},
            "T2": {"required_skills": ["Python"], "duration": 5, "deps": []},
            "T3": {"required_skills": ["Python", "ML"], "duration": 3, "deps": ["T1", "T2"]},
            "T4": {"required_skills": ["ML"], "duration": 2, "deps": ["T3"]}
        },
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
}

current_project_id = "project_alpha"

def get_current_project():
    global current_project_id
    if current_project_id not in projects:
        current_project_id = list(projects.keys())[0]
    return projects[current_project_id]
