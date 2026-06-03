from algorithms.topological_sort import topological_sort

def calculate_cpm(tasks: list, durations: dict, dependencies: dict) -> dict:
    """
    Perform the Critical Path Method (CPM) analysis on a set of tasks.
    
    Parameters:
    - tasks (list): List of task identifiers.
    - durations (dict): Dict mapping task identifier -> duration (numeric).
    - dependencies (dict): Dict mapping task identifier -> list of dependency task identifiers.
    
    Returns:
    - dict: A dictionary containing:
        - "es": dict of Early Start times
        - "ef": dict of Early Finish times
        - "ls": dict of Late Start times
        - "lf": dict of Late Finish times
        - "slack": dict of Slack/Float times
        - "critical_tasks": list of critical task identifiers (slack = 0), sorted topologically
        - "project_duration": float/int of total project duration
    
    Raises:
    - ValueError: If a cycle exists in the task dependencies.
    """
    if not tasks:
        return {
            "es": {}, "ef": {}, "ls": {}, "lf": {}, "slack": {},
            "critical_tasks": [], "project_duration": 0
        }

    # 1. Clean durations and dependencies
    cleaned_durations = {t: durations.get(t, 0) for t in tasks}
    cleaned_dependencies = {t: [dep for dep in dependencies.get(t, []) if dep in tasks] for t in tasks}
    
    # 2. Get topological order
    topo_order = topological_sort(tasks, cleaned_dependencies)
    
    # 3. Forward Pass: Calculate ES and EF
    es = {}
    ef = {}
    
    for task in topo_order:
        preds = cleaned_dependencies[task]
        if not preds:
            es[task] = 0
        else:
            es[task] = max(ef[pred] for pred in preds)
        ef[task] = es[task] + cleaned_durations[task]
        
    # Project duration is the maximum EF of all tasks
    project_duration = max(ef.values()) if ef else 0
    
    # 4. Backward Pass: Calculate LF and LS
    # Build successor lookup: task -> list of tasks that depend on it
    successors = {t: [] for t in tasks}
    for task in tasks:
        for pred in cleaned_dependencies[task]:
            successors[pred].append(task)
            
    ls = {}
    lf = {}
    
    # Process in reverse topological order
    for task in reversed(topo_order):
        succs = successors[task]
        if not succs:
            lf[task] = project_duration
        else:
            lf[task] = min(ls[succ] for succ in succs)
        ls[task] = lf[task] - cleaned_durations[task]
        
    # 5. Calculate Slack and identify critical tasks
    slack = {}
    critical_tasks = []
    
    for task in topo_order:
        # Slack = LF - EF or LS - ES
        # We round to 9 decimal places to avoid floating point issues
        slack_val = round(lf[task] - ef[task], 9)
        if isinstance(slack_val, float) and slack_val.is_integer():
            slack_val = int(slack_val)
        slack[task] = slack_val
        
        if slack_val == 0:
            critical_tasks.append(task)
            
    return {
        "es": es,
        "ef": ef,
        "ls": ls,
        "lf": lf,
        "slack": slack,
        "critical_tasks": critical_tasks,
        "project_duration": project_duration
    }

def critical_path(tasks: dict, topo_order: list) -> tuple:
    """
    User-specified simplified critical path logic.
    Computes earliest finish times, project duration, and critical tasks.
    """
    earliest_finish = {}

    for task in topo_order:
        deps = tasks[task]["deps"]
        if not deps:
            earliest_finish[task] = tasks[task]["duration"]
        else:
            max_prev = max(earliest_finish[d] for d in deps)
            earliest_finish[task] = max_prev + tasks[task]["duration"]

    project_duration = max(earliest_finish.values()) if earliest_finish else 0
    critical_tasks = []

    for task, finish in earliest_finish.items():
        if finish == project_duration:
            critical_tasks.append(task)

    return earliest_finish, project_duration, critical_tasks
