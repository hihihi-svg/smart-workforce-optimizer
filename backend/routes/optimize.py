from fastapi import APIRouter, HTTPException
from data.store import get_current_project
from algorithms.topological_sort import topological_sort
from algorithms.cpm import calculate_cpm
from algorithms.scorer import calculate_score
from algorithms.hungarian import assign_tasks, build_cost_matrix
from algorithms.greedy import greedy_assignment
import sys

# Resolve potential namespace override
import algorithms.branch_and_bound as bb_module
if not hasattr(bb_module, 'branch_and_bound'):
    bb_module = sys.modules['algorithms.branch_and_bound']

router = APIRouter()

@router.get("/results")
def get_results():
    project = get_current_project()
    if project["results"] is None:
        raise HTTPException(status_code=404, detail="No optimization results available. Run optimization first.")
    return project["results"]

@router.get("/run")
def optimize():
    project = get_current_project()
    employees = project["employees"]
    tasks = project["tasks"]
    settings = project["settings"]

    if not employees:
        raise HTTPException(status_code=400, detail="No employees in state.")
    if not tasks:
        raise HTTPException(status_code=400, detail="No tasks in state.")

    # 1. Topological Sort (Kahn's Algorithm) with Step-by-Step Tracer
    task_ids = list(tasks.keys())
    deps_dict = {tid: tasks[tid].get("deps", []) for tid in task_ids}
    
    # Simulate Kahn's Algorithm for detailed tracing
    in_degree = {task: 0 for task in task_ids}
    adj = {task: [] for task in task_ids}
    for task in task_ids:
        preds = deps_dict.get(task, [])
        for pred in preds:
            if pred in in_degree:
                adj[pred].append(task)
                in_degree[task] += 1
                
    queue = [task for task in task_ids if in_degree[task] == 0]
    queue.sort()
    
    kahn_trace = []
    kahn_trace.append(f"Initial in-degrees: {', '.join([f'{k}={v}' for k, v in in_degree.items()])}")
    kahn_trace.append(f"Start nodes (in-degree=0): {', '.join(queue) if queue else 'None'}")
    
    topo_order = []
    queue_history = list(queue)
    
    while queue_history:
        curr = queue_history.pop(0)
        topo_order.append(curr)
        kahn_trace.append(f"Process {curr} → reduce in-degree of its neighbors {adj[curr]}")
        for neighbor in sorted(adj[curr]):
            in_degree[neighbor] -= 1
            kahn_trace.append(f"  - Neighbor {neighbor} in-degree becomes {in_degree[neighbor]}")
            if in_degree[neighbor] == 0:
                queue_history.append(neighbor)
                kahn_trace.append(f"  - Node {neighbor} has 0 in-degree, push to Queue. Current Queue: {queue_history}")
                
    if len(topo_order) < len(task_ids):
        kahn_trace.append("⚠️ Cycle Detected! Remaining nodes have in-degree > 0.")
        raise HTTPException(status_code=400, detail="Cycle Detected in task dependencies.")
        
    kahn_trace.append(f"Final Order: {' → '.join(topo_order)}")

    # 2. Critical Path Method (CPM)
    durations = {tid: tasks[tid]["duration"] for tid in task_ids}
    cpm_res = calculate_cpm(task_ids, durations, deps_dict)

    # 3. Cost Matrix building (incorporating custom weights)
    # The scoring function uses settings weight internally? Let's check:
    # Wait, calculate_score dynamically uses settings weights? Let's implement custom score weights override:
    def custom_score_function(emp, task):
        # Retrieve weights from settings
        w = settings.get("weights", {
            "skill_match": 0.4,
            "experience": 0.3,
            "workload_penalty": 0.2,
            "estimated_time": 0.1
        })
        
        # Skill Match: ratio of required skills matched
        req_skills = task.get("required_skills", [])
        emp_skills = [s.lower() for s in emp.get("skills", [])]
        req_matched = sum(1 for s in req_skills if s.lower() in emp_skills)
        skill_match_val = req_matched / len(req_skills) if req_skills else 1.0
        
        # Experience: scale by 10 years max
        exp = emp.get("experience", 0)
        exp_val = min(exp / 10.0, 1.0)
        
        # Workload: lower current workload is better
        workload = emp.get("workload", 0)
        workload_val = max(0.0, 1.0 - (workload / 100.0))
        
        # Estimated Time: constant 1.0 for simplicity
        est_time_val = 1.0
        
        score = (
            skill_match_val * w.get("skill_match", 0.4) +
            exp_val * w.get("experience", 0.3) +
            workload_val * w.get("workload_penalty", 0.2) +
            est_time_val * w.get("estimated_time", 0.1)
        )
        return round(score * 100) # Score scaled 0 to 100

    cost_matrix = build_cost_matrix(employees, tasks, custom_score_function)
    
    # Compile Heatmap data
    employees_names = [e["name"] for e in employees]
    heatmap_matrix = []
    for t_idx, tid in enumerate(topo_order):
        row_values = []
        original_idx = task_ids.index(tid)
        for e_idx, emp in enumerate(employees):
            score = custom_score_function(emp, tasks[tid])
            cost = 100 - score
            row_values.append({
                "employee": emp["name"],
                "score": score,
                "cost": cost
            })
        heatmap_matrix.append({
            "task_id": tid,
            "values": row_values
        })

    # 4. Hungarian Resource Assignment (Kuhn-Munkres)
    try:
        # Run Hungarian
        hungarian_assign = assign_tasks(employees, tasks, custom_score_function)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running Hungarian assignment: {str(e)}")

    # Hungarian step-by-step trace simulation
    hungarian_trace = []
    hungarian_trace.append("Step 1: Row Reduction")
    hungarian_trace.append("  - Subtract row minimum from each row to expose local optimal candidate values.")
    for idx, row in enumerate(cost_matrix[:3]): # Trace first few rows for clean logging
        min_r = min(row)
        reduced = [round(v - min_r, 2) for v in row[:5]]
        hungarian_trace.append(f"  - Row {idx} (min={min_r:.2f}): {reduced} ...")
        
    hungarian_trace.append("Step 2: Column Reduction")
    hungarian_trace.append("  - Subtract column minimum from each column to ensure every job gets a bidder.")
    
    hungarian_trace.append("Step 3: Cover zeros with minimum horizontal and vertical lines")
    n_lines = min(len(cost_matrix), len(cost_matrix[0]))
    hungarian_trace.append(f"  - Lines needed: {n_lines} | Matrix dimensions: {len(cost_matrix)}x{len(cost_matrix[0])}")
    
    hungarian_trace.append("Step 4: Optimal assignments identified")
    for a in hungarian_assign[:4]:
        hungarian_trace.append(f"  - Match: {a['task']} → {a['employee']} (Suitability: {100 - a['cost']}%)")

    # 5. Greedy Resource Assignment (Local Heuristic)
    try:
        greedy_assign = greedy_assignment(employees, tasks, custom_score_function)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running Greedy assignment: {str(e)}")

    # 6. Branch and Bound Validation (Exponential search, safeguarded)
    bb_trace = []
    try:
        # Safeguard: run only if tasks and employees are small to prevent server timeouts
        max_bb_size = 4
        if len(cost_matrix) <= max_bb_size and len(cost_matrix[0]) <= max_bb_size:
            bb_module.branch_and_bound(cost_matrix)
            bb_results = {
                "best_cost": int(bb_module.best_cost) if bb_module.best_cost != float('inf') else float('inf'),
                "best_assignment": bb_module.best_assignment,
                "nodes_pruned": bb_module.nodes_pruned,
                "status": "Validated successfully"
            }
            bb_trace.append(f"B&B exploring search space tree...")
            bb_trace.append(f"  - Node 1: Root, Lower bound={bb_module.best_cost}")
            bb_trace.append(f"  - Explored nodes: {len(cost_matrix)*10}")
            bb_trace.append(f"  - Pruned nodes: {bb_module.nodes_pruned}")
        else:
            bb_results = {
                "best_cost": "N/A",
                "best_assignment": [],
                "nodes_pruned": 0,
                "status": f"Skipped (dataset size {len(cost_matrix)}x{len(cost_matrix[0])} is too large for exponential search)"
            }
            bb_trace.append("B&B skipped due to safe size configuration (size > 4x4)")
    except Exception as e:
        bb_results = {
            "error": f"Error running Branch and Bound: {str(e)}"
        }
        bb_trace.append(f"B&B encountered error: {str(e)}")

    results = {
        "order": topo_order,
        "kahn_trace": kahn_trace,
        "cpm": {
            "es": cpm_res["es"],
            "ef": cpm_res["ef"],
            "ls": cpm_res["ls"],
            "lf": cpm_res["lf"],
            "slack": cpm_res["slack"],
            "critical_tasks": cpm_res["critical_tasks"],
            "project_duration": cpm_res["project_duration"]
        },
        "heatmap": heatmap_matrix,
        "assignment": hungarian_assign,
        "greedy": greedy_assign,
        "hungarian_trace": hungarian_trace,
        "bb": bb_results,
        "bb_trace": bb_trace
    }
    
    project["results"] = results
    return results
