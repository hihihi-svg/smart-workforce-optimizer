from fastapi import APIRouter, HTTPException
from data.store import employees, tasks
from algorithms.topological_sort import topological_sort
from algorithms.cpm import critical_path
from algorithms.scorer import calculate_score
from algorithms.hungarian import assign_tasks, build_cost_matrix
from algorithms.greedy import greedy_assignment
import sys

# Resolve potential namespace override where the package exposes the function instead of the module
import algorithms.branch_and_bound as bb_module
if not hasattr(bb_module, 'branch_and_bound'):
    bb_module = sys.modules['algorithms.branch_and_bound']

router = APIRouter()

@router.get("/run")
def optimize():
    if not employees:
        raise HTTPException(status_code=400, detail="No employees in state.")
    if not tasks:
        raise HTTPException(status_code=400, detail="No tasks in state.")

    # 1. Topological Sort (Kahn's Algorithm)
    topo_order = topological_sort(tasks)
    if topo_order == "Cycle Detected":
        raise HTTPException(status_code=400, detail="Cycle Detected in task dependencies.")

    # 2. Critical Path Method (CPM)
    try:
        earliest_finish, duration, critical_tasks = critical_path(tasks, topo_order)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running CPM: {str(e)}")

    # 3. Hungarian Resource Assignment (Kuhn-Munkres)
    try:
        hungarian_assign = assign_tasks(employees, tasks, calculate_score)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running Hungarian assignment: {str(e)}")

    # 4. Greedy Resource Assignment (Local Heuristic)
    try:
        greedy_assign = greedy_assignment(employees, tasks, calculate_score)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running Greedy assignment: {str(e)}")

    # 5. Branch and Bound Validation (Exponential worst-case, safeguarded for large datasets)
    try:
        cost_matrix = build_cost_matrix(employees, tasks, calculate_score)
        
        # Safeguard: run only if tasks and employees are small (<= 4) to prevent server timeouts
        if len(cost_matrix) <= 4 and len(cost_matrix[0]) <= 4:
            bb_module.branch_and_bound(cost_matrix)
            bb_results = {
                "best_cost": int(bb_module.best_cost) if bb_module.best_cost != float('inf') else float('inf'),
                "best_assignment": bb_module.best_assignment,
                "nodes_pruned": bb_module.nodes_pruned,
                "status": "Validated successfully"
            }
        else:
            bb_results = {
                "best_cost": "N/A",
                "best_assignment": [],
                "nodes_pruned": 0,
                "status": f"Skipped (dataset size {len(cost_matrix)}x{len(cost_matrix[0])} is too large for exponential search)"
            }
    except Exception as e:
        bb_results = {
            "error": f"Error running Branch and Bound: {str(e)}"
        }

    return {
        "order": topo_order,
        "cpm": {
            "earliest_finish": earliest_finish,
            "duration": duration,
            "critical_tasks": critical_tasks
        },
        "assignment": hungarian_assign,
        "greedy": greedy_assign,
        "bb": bb_results
    }
