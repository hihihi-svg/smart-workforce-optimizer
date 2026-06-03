def greedy_assignment(
    matrix_or_employees, 
    tasks: list = None, 
    score_function = None, 
    maximize: bool = True
):
    """
    Polymorphic Greedy Assignment Solver.
    
    Supports:
    1. Employee-Task list signature: greedy_assignment(employees, tasks, score_function)
    2. 2D Score Matrix signature: greedy_assignment(matrix, maximize=True)
    """
    if tasks is not None and score_function is not None:
        if isinstance(tasks, dict):
            tasks_list = []
            for task_id, task_info in tasks.items():
                t_copy = dict(task_info)
                t_copy["id"] = task_id
                tasks_list.append(t_copy)
            tasks = tasks_list
            
        employees = matrix_or_employees
        available = employees.copy()
        assignments = []
        for task in tasks:
            best_employee = None
            best_score = -999999
            for emp in available:
                score = score_function(emp, task)
                if score > best_score:
                    best_score = score
                    best_employee = emp
            if best_employee:
                assignments.append({
                    "task": task["id"],
                    "employee": best_employee["name"],
                    "score": round(best_score, 2)
                })
                available.remove(best_employee)
        return assignments

    # Fallback to 2D matrix matching
    matrix = matrix_or_employees
    if not matrix or not matrix[0]:
        return [], 0

    num_rows = len(matrix)
    num_cols = len(matrix[0])

    # 1. Collect all candidates
    candidates = []
    for r in range(num_rows):
        for c in range(num_cols):
            candidates.append((matrix[r][c], r, c))

    # 2. Sort candidates based on criteria
    # Maximize: sort descending. Minimize: sort ascending.
    candidates.sort(key=lambda x: x[0], reverse=maximize)

    # 3. Match greedily
    assignments = []
    assigned_rows = set()
    assigned_cols = set()
    total_value = 0.0

    for value, r, c in candidates:
        # If we have reached maximum possible matches, we can stop
        if len(assignments) == min(num_rows, num_cols):
            break
            
        if r not in assigned_rows and c not in assigned_cols:
            assignments.append((r, c))
            assigned_rows.add(r)
            assigned_cols.add(c)
            total_value += value

    # Sort assignments by row index for consistency
    assignments.sort(key=lambda x: x[0])
    
    # Format total value as integer if appropriate
    is_all_int = all(all(isinstance(val, int) or float(val).is_integer() for val in row) for row in matrix)
    if is_all_int:
        total_value = int(total_value)

    return assignments, total_value


def greedy_interval_scheduling(tasks_intervals: list) -> list:
    """
    Solve the Interval Scheduling Problem to find the maximum set of mutually
    compatible tasks (no overlapping time intervals).
    
    Uses the optimal greedy choice: Earliest Finish Time (EFT) first.
    
    Parameters:
    - tasks_intervals (list of dicts): List of tasks, where each task is:
        {
            "id": task_id,
            "start": start_time (numeric),
            "end": end_time (numeric)
        }
        
    Returns:
    - list: List of selected task dicts.
    """
    if not tasks_intervals:
        return []

    # Filter out invalid intervals and sort by finish time ('end') ascending
    # Tie-breaker: start time descending (to pick shorter tasks if they end at the same time)
    sorted_tasks = sorted(
        [t for t in tasks_intervals if t.get("end", 0) >= t.get("start", 0)],
        key=lambda x: (x.get("end", 0), -x.get("start", 0))
    )

    selected_tasks = []
    last_end_time = -float('inf')

    for task in sorted_tasks:
        start = task.get("start", 0)
        # If the task starts after or when the last scheduled task ends, select it
        if start >= last_end_time:
            selected_tasks.append(task)
            last_end_time = task.get("end", 0)

    return selected_tasks
