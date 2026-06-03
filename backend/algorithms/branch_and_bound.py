from algorithms.heap import MaxHeap

class KnapsackNode:
    def __init__(self, level, value, weight, bound, selected_indices):
        self.level = level
        self.value = value
        self.weight = weight
        self.bound = bound
        self.selected_indices = selected_indices  # Tuple of indices in sorted list

def solve_knapsack_branch_and_bound(values: list, weights: list, capacity: float) -> tuple:
    """
    Solve the 0/1 Knapsack Problem using Branch & Bound (Best-First Search).
    Selects a subset of items to maximize total value without exceeding capacity.
    
    Parameters:
    - values (list): List of numerical values (utility/score) for each item.
    - weights (list): List of numerical weights (cost/time) for each item.
    - capacity (float): The maximum capacity (budget/time limit).
    
    Returns:
    - tuple: (max_value, selected_original_indices)
        - max_value: The optimized total value.
        - selected_original_indices: List of original 0-based indices of chosen items.
    """
    n = len(values)
    if n == 0 or capacity <= 0:
        return 0, []

    # 1. Package items with their original index and sort by value/weight ratio descending
    items = []
    for i in range(n):
        v = float(values[i])
        w = float(weights[i])
        ratio = v / w if w > 0 else float('inf')
        items.append((v, w, i, ratio))

    # Sort descending by ratio
    items.sort(key=lambda x: x[3], reverse=True)
    
    sorted_values = [item[0] for item in items]
    sorted_weights = [item[1] for item in items]
    original_indices = [item[2] for item in items]

    # Helper function to calculate upper bound of value for a node
    def get_bound(node: KnapsackNode) -> float:
        if node.weight >= capacity:
            return 0.0
            
        value_bound = node.value
        total_weight = node.weight
        j = node.level + 1
        
        # Greedily add next items
        while j < n and total_weight + sorted_weights[j] <= capacity:
            total_weight += sorted_weights[j]
            value_bound += sorted_values[j]
            j += 1
            
        # Add fractional part of next item if there is room
        if j < n:
            remaining_capacity = capacity - total_weight
            value_bound += remaining_capacity * (sorted_values[j] / sorted_weights[j])
            
        return value_bound

    # 2. Initialize search
    max_value = 0.0
    best_selected_sorted = ()
    
    # Priority Queue of nodes, sorted by bound (MaxHeap)
    pq = MaxHeap()
    
    # Root node: level = -1, value = 0, weight = 0, selected = ()
    root = KnapsackNode(level=-1, value=0.0, weight=0.0, bound=0.0, selected_indices=())
    root.bound = get_bound(root)
    
    pq.push(root, root.bound)
    
    while not pq.is_empty():
        # Pop the node with the highest bound
        curr_node, _ = pq.pop()
        
        # If the node's bound is promising (better than max value found so far)
        if curr_node.bound > max_value:
            next_level = curr_node.level + 1
            
            if next_level < n:
                # --- branch 1: INCLUDE next item ---
                next_w = curr_node.weight + sorted_weights[next_level]
                next_v = curr_node.value + sorted_values[next_level]
                next_sel = curr_node.selected_indices + (next_level,)
                
                if next_w <= capacity:
                    if next_v > max_value:
                        max_value = next_v
                        best_selected_sorted = next_sel
                        
                    # Create node and push if its bound is promising
                    left_node = KnapsackNode(
                        level=next_level,
                        value=next_v,
                        weight=next_w,
                        bound=0.0,
                        selected_indices=next_sel
                    )
                    left_node.bound = get_bound(left_node)
                    if left_node.bound > max_value:
                        pq.push(left_node, left_node.bound)
                
                # --- branch 2: EXCLUDE next item ---
                right_node = KnapsackNode(
                    level=next_level,
                    value=curr_node.value,
                    weight=curr_node.weight,
                    bound=0.0,
                    selected_indices=curr_node.selected_indices
                )
                right_node.bound = get_bound(right_node)
                if right_node.bound > max_value:
                    pq.push(right_node, right_node.bound)

    # Convert sorted selection back to original indices
    selected_orig = [original_indices[idx] for idx in best_selected_sorted]
    selected_orig.sort()
    
    # Format return types
    is_all_int = all(isinstance(v, int) or float(v).is_integer() for v in values)
    if is_all_int:
        max_value = int(max_value)
        
    return max_value, selected_orig

# Globals for user-specified branch_and_bound solver
best_cost = float('inf')
best_assignment = []
nodes_pruned = 0

def branch_and_bound(
    matrix: list,
    row: int = 0,
    used: set = None,
    current_cost: float = 0,
    current_assign: list = None
):
    """
    Branch and Bound solver for Linear Assignment cost minimization.
    Matches the user's specific recursive search pattern.
    """
    global best_cost
    global best_assignment
    global nodes_pruned

    # Reset globals on initial invocation to prevent state leakage
    if row == 0 and (used is None or len(used) == 0):
        best_cost = float('inf')
        best_assignment = []
        nodes_pruned = 0

    if used is None:
        used = set()

    if current_assign is None:
        current_assign = []

    # Prune branch if the current cost exceeds the best cost found so far
    if current_cost >= best_cost:
        nodes_pruned += 1
        return

    # If all rows have been assigned, update the best solution
    if row == len(matrix):
        if current_cost < best_cost:
            best_cost = current_cost
            best_assignment = current_assign.copy()
        return

    # Branch on all available columns for the current row
    for col in range(len(matrix[0])):
        if col not in used:
            used.add(col)
            current_assign.append((row, col))
            
            branch_and_bound(
                matrix,
                row + 1,
                used,
                current_cost + matrix[row][col],
                current_assign
            )
            
            used.remove(col)
            current_assign.pop()
