def calculate_suitability_score(
    employee: dict, 
    task: dict, 
    weights: dict = None
) -> float:
    """
    Calculate a compatibility score (0.0 to 100.0) between an employee and a task.
    
    Parameters:
    - employee (dict): Contains employee details:
        - "skills": dict of skill_name -> level (int 1 to 5)
        - "hourly_rate": numeric rate
        - "availability": float (0.0 to 1.0 representing work capacity/availability)
    - task (dict): Contains task requirements:
        - "required_skills": dict of skill_name -> minimum_level (int 1 to 5) OR list of skill names
        - "budget_rate": numeric target hourly rate
    - weights (dict): Optional dict for custom weighting:
        - "skill": weight of skill matching (default: 0.6)
        - "cost": weight of cost alignment (default: 0.3)
        - "availability": weight of availability (default: 0.1)
        
    Returns:
    - float: Suitability score from 0.0 to 100.0.
    """
    if weights is None:
        weights = {"skill": 0.6, "cost": 0.3, "availability": 0.1}

    # Normalize weights so they sum to 1.0
    total_w = sum(weights.values())
    w_skill = weights.get("skill", 0.6) / total_w
    w_cost = weights.get("cost", 0.3) / total_w
    w_avail = weights.get("availability", 0.1) / total_w

    # 1. Calculate Skill Match Score (0.0 to 100.0)
    emp_skills = employee.get("skills", {})
    req_skills = task.get("required_skills", {})
    
    if not req_skills:
        skill_score = 100.0
    else:
        # Support both dictionary of required skill -> level, and simple list of skill names
        if isinstance(req_skills, list):
            req_skills = {skill: 1 for skill in req_skills}
            
        total_skills_needed = len(req_skills)
        cumulative_match = 0.0
        
        for skill, req_level in req_skills.items():
            # Handle case-insensitive matching
            emp_level = 0
            for emp_sk, emp_lvl in emp_skills.items():
                if emp_sk.lower() == skill.lower():
                    emp_level = emp_lvl
                    break
            
            if emp_level >= req_level:
                # Meets or exceeds requirements
                cumulative_match += 1.0
            elif emp_level > 0:
                # Partially matches requirements
                cumulative_match += float(emp_level) / float(req_level)
            else:
                # Skill is missing entirely
                cumulative_match += 0.0
                
        skill_score = (cumulative_match / total_skills_needed) * 100.0

    # 2. Calculate Cost Score (0.0 to 100.0)
    emp_rate = float(employee.get("hourly_rate", 0))
    target_rate = float(task.get("budget_rate", 0))
    
    if emp_rate <= 0:
        cost_score = 100.0
    elif target_rate <= 0:
        cost_score = 0.0
    elif emp_rate <= target_rate:
        # Under or at budget
        cost_score = 100.0
    else:
        # Over budget - score decreases exponentially or linearly
        # Let's use simple linear decay ratio
        cost_score = max(0.0, (target_rate / emp_rate) * 100.0)

    # 3. Calculate Availability Score (0.0 to 100.0)
    # Availability is already defined as 0.0 to 1.0
    avail_score = float(employee.get("availability", 1.0)) * 100.0

    # 4. Compute weighted final score
    final_score = (w_skill * skill_score) + (w_cost * cost_score) + (w_avail * avail_score)
    return round(final_score, 2)


def generate_suitability_matrix(employees: list, tasks: list, weights: dict = None) -> list:
    """
    Generate a 2D suitability matrix where matrix[i][j] is the compatibility score
    between employees[i] and tasks[j].
    
    Parameters:
    - employees (list of dicts): List of employee profiles.
    - tasks (list of dicts): List of tasks.
    - weights (dict): Custom weights.
    
    Returns:
    - list of lists: 2D matrix of scores.
    """
    matrix = []
    for emp in employees:
        row = []
        for t in tasks:
            score = calculate_suitability_score(emp, t, weights)
            row.append(score)
        matrix.append(row)
    return matrix

def calculate_score(employee: dict, task: dict) -> float:
    """
    User-specified experience and workload based scoring formula.
    """
    required = set(task["required_skills"])
    employee_skills = set(employee["skills"])
    
    matched = len(required & employee_skills)
    skill_score = (matched / len(required)) * 40 if required else 40.0
    
    experience_score = employee.get("experience", 0) * 5
    workload_penalty = employee.get("workload", 0) * 0.3
    duration_penalty = task.get("duration", 0) * 2
    
    final_score = skill_score + experience_score - workload_penalty - duration_penalty
    return round(final_score, 2)
