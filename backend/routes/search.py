from fastapi import APIRouter, HTTPException
from algorithms.trie import Trie
from data.store import get_current_project
from algorithms.scorer import calculate_score
import heapq

router = APIRouter()

@router.get("/skill/{prefix}")
def search_skill(prefix: str):
    project = get_current_project()
    employees = project["employees"]
    
    # Dynamically build the Trie from the current in-memory employee records of the active project
    trie = Trie()
    for emp in employees:
        for skill in emp.get("skills", []):
            trie.insert(skill.lower(), emp["name"])
            
    # Search the prefix in the Trie to find matched names
    matched_names = trie.search_prefix(prefix.lower())
    
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

@router.get("/candidates/{task_id}")
def find_candidates(task_id: str, k: int = 3):
    project = get_current_project()
    employees = project["employees"]
    tasks = project["tasks"]
    settings = project["settings"]
    
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
        
    task = tasks[task_id]
    required_skills = task.get("required_skills", [])
    
    # Build a trace log to show the step-by-step visual pipeline
    trace = []
    trace.append(f"Step 1: Task '{task_id}' requires skills → {', '.join(required_skills)}")
    
    # Construct Trie
    trie = Trie()
    for emp in employees:
        for skill in emp.get("skills", []):
            trie.insert(skill.lower(), emp["name"])
            
    # Step 2: Trie search per skill
    trie_matches = {}
    for skill in required_skills:
        names = trie.search_prefix(skill.lower())
        trie_matches[skill] = names
        trace.append(f"Step 2: Trie.search('{skill}') matched → {', '.join(names) if names else 'None'}")
        
    # Step 3: Intersection of matches
    if required_skills:
        intersected = set(trie_matches.get(required_skills[0], []))
        for skill in required_skills[1:]:
            intersected = intersected.intersection(trie_matches.get(skill, []))
    else:
        intersected = set([emp["name"] for emp in employees])
        
    trace.append(f"Step 3: Intersection of skill matches → {', '.join(intersected) if intersected else 'None'}")
    
    # Map to employee records
    candidates = [emp for emp in employees if emp["name"] in intersected]
    
    # Step 4: Filter availability
    # Wait, some employees might not have an explicit availability flag, let's assume they are available by default
    # If settings["availability_filter"] is on, we filter out any employee with availability = false.
    available_candidates = []
    availability_filter_on = settings.get("availability_filter", True)
    for c in candidates:
        if availability_filter_on and c.get("availability") == False:
            trace.append(f"Step 4: Filter availability → Excluded {c['name']} (Unavailable)")
        else:
            available_candidates.append(c)
            
    trace.append(f"Step 4: Available candidates count → {len(available_candidates)}")
    
    # Step 5: Filter workload
    max_workload = settings.get("max_workload", 80)
    eligible_candidates = []
    for c in available_candidates:
        if c.get("workload", 0) > max_workload:
            trace.append(f"Step 5: Filter workload < {max_workload}% → Excluded {c['name']} (Workload {c['workload']}% exceeds threshold)")
        else:
            eligible_candidates.append(c)
            
    trace.append(f"Step 5: Eligible candidates count → {len(eligible_candidates)}")
    
    # Step 6: Score each candidate
    # Retrieve scoring weights
    weights = settings.get("weights", {
        "skill_match": 0.4,
        "experience": 0.3,
        "workload_penalty": 0.2,
        "estimated_time": 0.1
    })
    
    scored_candidates = []
    score_breakdowns = {}
    
    trace.append("Step 6: Score each eligible candidate:")
    for c in eligible_candidates:
        # Calculate components
        # Skill Match: ratio of required skills matched
        emp_skills_lower = [s.lower() for s in c.get("skills", [])]
        req_matched = sum(1 for s in required_skills if s.lower() in emp_skills_lower)
        skill_match_val = req_matched / len(required_skills) if required_skills else 1.0
        
        # Experience component: log or scale by max exp (say, 10 years max reference)
        exp = c.get("experience", 0)
        exp_val = min(exp / 10.0, 1.0)
        
        # Workload penalty component: penalty proportional to current workload
        workload = c.get("workload", 0)
        workload_val = max(0.0, 1.0 - (workload / 100.0))
        
        # Estimated time component: assume lower duration tasks or similar factors, let's keep it simple as base 1.0
        est_time_val = 1.0
        
        # Calculate final score
        score = (
            skill_match_val * weights.get("skill_match", 0.4) +
            exp_val * weights.get("experience", 0.3) +
            workload_val * weights.get("workload_penalty", 0.2) +
            est_time_val * weights.get("estimated_time", 0.1)
        )
        
        # Ensure precision
        score = round(score, 2)
        
        scored_candidates.append((score, c["name"]))
        score_breakdowns[c["name"]] = {
            "score": score,
            "skill_match": f"{skill_match_val:.2f} * {weights.get('skill_match'):.1f} = {skill_match_val * weights.get('skill_match'):.2f}",
            "experience": f"{exp_val:.2f} * {weights.get('experience'):.1f} = {exp_val * weights.get('experience'):.2f}",
            "workload_penalty": f"{workload_val:.2f} * {weights.get('workload_penalty'):.1f} = {workload_val * weights.get('workload_penalty'):.2f}",
            "est_time": f"{est_time_val:.2f} * {weights.get('estimated_time'):.1f} = {est_time_val * weights.get('estimated_time'):.2f}"
        }
        
        trace.append(f"  - {c['name']}: Match={skill_match_val:.2f}, Exp={exp} yrs, Load={workload}%, Score={score}")
        
    # Heap top-K extraction animation trace simulation
    trace.append("Step 7: Min-Heap Animation Trace (K-size constraint check):")
    heap = []
    for score, name in scored_candidates:
        if len(heap) < k:
            heapq.heappush(heap, (score, name))
            trace.append(f"  - Push ({score}, {name}) → Heap: {[(s, n) for s, n in heap]}")
        else:
            min_score, min_name = heap[0]
            if score > min_score:
                heapq.heappop(heap)
                heapq.heappush(heap, (score, name))
                trace.append(f"  - Score {score} > Heap minimum {min_score} ({min_name}) → Eject {min_name}, Push {name} → Heap: {[(s, n) for s, n in heap]}")
            else:
                trace.append(f"  - Score {score} <= Heap minimum {min_score} ({min_name}) → Ignore {name}")
                
    # Sort descending for top list
    top_candidates_list = sorted(heap, reverse=True, key=lambda x: x[0])
    
    # Map back to full profiles
    results = []
    for score, name in top_candidates_list:
        emp_profile = next(emp for emp in employees if emp["name"] == name)
        results.append({
            "employee": emp_profile,
            "score": score,
            "breakdown": score_breakdowns[name]
        })
        
    return {
        "task_id": task_id,
        "required_skills": required_skills,
        "trace": trace,
        "top_candidates": results
    }
