def topological_sort(tasks, dependencies: dict = None) -> list:
    """
    Perform a topological sort on tasks based on their dependencies using Kahn's Algorithm.
    
    Parameters:
    - tasks (list or dict): A list of task identifiers, OR a dictionary mapping task identifiers to their list of dependencies.
    - dependencies (dict, optional): A dictionary mapping a task identifier to its dependencies (if tasks is a list).
    
    Returns:
    - list or str: A topologically sorted list of task identifiers, or "Cycle Detected" (if tasks is a dict).
    
    Raises:
    - ValueError: If a cycle is detected and tasks was passed as a list.
    """
    single_arg_mode = False
    if dependencies is None:
        if isinstance(tasks, dict):
            dependencies = tasks
            tasks = list(tasks.keys())
            single_arg_mode = True
        else:
            dependencies = {}

    # 1. Initialize structures
    in_degree = {task: 0 for task in tasks}
    adj = {task: [] for task in tasks}
    
    # 2. Build graph and compute in-degrees
    for task in tasks:
        # Get predecessors/dependencies for the current task
        preds = dependencies.get(task, [])
        if isinstance(preds, dict):
            preds = preds.get("deps", []) or preds.get("dependencies", [])
        for pred in preds:
            # We only build edges between tasks that are part of our task list
            if pred in in_degree:
                adj[pred].append(task)
                in_degree[task] += 1
            else:
                # If dependency is not in task list, it acts as a external dependency.
                # Since we don't track it, we don't increment in-degree or add edges.
                pass
                
    # 3. Find all nodes with in-degree 0
    # Sort them to make the topological sort deterministic and neat
    queue = [task for task in tasks if in_degree[task] == 0]
    # Keep queue sorted alphabetically/numerically for deterministic behavior
    queue.sort() 
    
    sorted_order = []
    
    # 4. Process queue
    while queue:
        # Pop from the front to maintain queue behavior (FIFO)
        curr = queue.pop(0)
        sorted_order.append(curr)
        
        # Decrement in-degree for all neighbors (successors)
        # Sort neighbors for deterministic execution order
        for neighbor in sorted(adj[curr]):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
                
    # 5. Cycle detection
    if len(sorted_order) < len(tasks):
        if single_arg_mode:
            return "Cycle Detected"
        # Identify nodes that participate in the cycle
        cycle_nodes = [task for task, degree in in_degree.items() if degree > 0]
        raise ValueError(f"Cycle detected in task dependencies involving: {cycle_nodes}")
        
    return sorted_order
