from scipy.optimize import linear_sum_assignment

def solve_hungarian(matrix: list, maximize: bool = False) -> tuple:
    """
    Solve the Linear Assignment Problem using the Hungarian (Kuhn-Munkres) Algorithm.
    Implemented from scratch in pure Python.
    
    Parameters:
    - matrix (list of lists): 2D cost or scoring matrix.
    - maximize (bool): If True, finds the assignment that maximizes the sum of elements
                        (e.g., matching suitability scores). If False, minimizes cost.
                        
    Returns:
    - tuple: (assignments, total_value)
        - assignments: list of tuples (row_idx, col_idx) representing the optimal assignment.
        - total_value: sum of the selected elements in the original matrix.
    """
    if not matrix or not matrix[0]:
        return [], 0

    num_rows = len(matrix)
    num_cols = len(matrix[0])
    max_dim = max(num_rows, num_cols)

    # 1. Transform matrix for maximization if required
    # Also find global min to shift any negative values to non-negative
    original = [[float(val) for val in row] for row in matrix]
    
    if maximize:
        max_val = max(max(row) for row in original)
        # For maximization, cost = max_val - original_val
        cost_matrix = [[max_val - val for val in row] for row in original]
    else:
        min_val = min(min(row) for row in original)
        if min_val < 0:
            # Shift all values to be non-negative
            cost_matrix = [[val - min_val for val in row] for row in original]
        else:
            cost_matrix = [[val for val in row] for row in original]

    # 2. Pad the cost matrix to make it square (max_dim x max_dim)
    # Pad dummy rows and columns with 0 cost. This allows dummy workers/tasks to
    # be matched without adding cost, leaving the real matching optimized.
    padded_matrix = [[0.0 for _ in range(max_dim)] for _ in range(max_dim)]
    for r in range(num_rows):
        for c in range(num_cols):
            padded_matrix[r][c] = cost_matrix[r][c]

    # Run the Munkres algorithm on the padded square matrix
    starred_zeros = _run_munkres(padded_matrix)

    # 3. Extract assignments (filter out any padded dummy assignments)
    assignments = []
    total_value = 0.0
    for r, c in starred_zeros:
        if r < num_rows and c < num_cols:
            assignments.append((r, c))
            total_value += original[r][c]

    # Sort assignments by row index for neatness
    assignments.sort(key=lambda x: x[0])
    
    # If original values were integers, return total value as integer
    # (since streamlit / display looks cleaner with ints when appropriate)
    is_all_int = all(all(val.is_integer() for val in row) for row in original)
    if is_all_int:
        total_value = int(total_value)

    return assignments, total_value


def _run_munkres(C: list) -> list:
    """
    Internal helper implementing the Munkres (Hungarian) algorithm on a square matrix C.
    Returns a list of (row, col) coordinates of the starred zeros.
    """
    n = len(C)
    
    # State tracking
    # marked[r][c] values: 0 = normal, 1 = starred (*), 2 = primed (')
    marked = [[0 for _ in range(n)] for _ in range(n)]
    row_covered = [False] * n
    col_covered = [False] * n

    # Step 1: Subtract row minimums
    for r in range(n):
        row_min = min(C[r])
        for c in range(n):
            C[r][c] -= row_min

    # Step 2: Find a zero (Z) in C. Star Z if there are no other starred zeros
    # in its row or column.
    for r in range(n):
        for c in range(n):
            if C[r][c] == 0 and not row_covered[r] and not col_covered[c]:
                marked[r][c] = 1
                row_covered[r] = True
                col_covered[c] = True

    # Reset covered arrays for the main loop
    row_covered = [False] * n
    col_covered = [False] * n

    # Step 3: Cover columns containing starred zeros
    for r in range(n):
        for c in range(n):
            if marked[r][c] == 1:
                col_covered[c] = True

    step = 4
    path_start_row = 0
    path_start_col = 0

    # Main loop state machine
    while step != 7:
        if step == 4:
            # Step 4: Find an uncovered zero and prime it.
            zero_row, zero_col = _find_a_zero(C, row_covered, col_covered)
            if zero_row == -1:
                # No uncovered zeros left. Find the minimum uncovered value.
                step = 6
            else:
                marked[zero_row][zero_col] = 2 # Prime it
                # Find starred zero in the same row
                star_col = _find_star_in_row(marked, zero_row)
                if star_col != -1:
                    # Cover this row, uncover the column of the starred zero
                    row_covered[zero_row] = True
                    col_covered[star_col] = False
                    # Repeat Step 4
                    step = 4
                else:
                    # No starred zero in this row. Go to Step 5.
                    path_start_row = zero_row
                    path_start_col = zero_col
                    step = 5

        elif step == 5:
            # Step 5: Construct alternating path of primed and starred zeros
            # path list stores (row, col)
            path = [(path_start_row, path_start_col)]
            
            while True:
                # Find starred zero in the column of the last path element
                r_star = _find_star_in_col(marked, path[-1][1])
                if r_star == -1:
                    break
                path.append((r_star, path[-1][1]))
                
                # Find primed zero in the row of the starred zero
                c_prime = _find_prime_in_row(marked, r_star)
                path.append((r_star, c_prime))

            # Augment path: unstar stars, star primes
            for r, c in path:
                if marked[r][c] == 1:
                    marked[r][c] = 0 # Unstar
                elif marked[r][c] == 2:
                    marked[r][c] = 1 # Star

            # Clear all primes and covers
            for r in range(n):
                for c in range(n):
                    if marked[r][c] == 2:
                        marked[r][c] = 0
            row_covered = [False] * n
            col_covered = [False] * n

            # Cover columns of starred zeros
            for r in range(n):
                for c in range(n):
                    if marked[r][c] == 1:
                        col_covered[c] = True
            
            # Check if we have n covered columns (all matched)
            if sum(col_covered) == n:
                step = 7 # Done
            else:
                step = 4

        elif step == 6:
            # Step 6: Find minimum uncovered value, subtract it from uncovered,
            # and add to double covered (intersections).
            min_val = _find_smallest_uncovered(C, row_covered, col_covered)
            if min_val == float('inf'):
                # Avoid infinite loop if all are covered
                step = 7
                break
                
            for r in range(n):
                for c in range(n):
                    if row_covered[r]:
                        C[r][c] += min_val
                    if not col_covered[c]:
                        C[r][c] -= min_val
            step = 4

    # Compile the final assignments from starred zeros
    starred_positions = []
    for r in range(n):
        for c in range(n):
            if marked[r][c] == 1:
                starred_positions.append((r, c))
    return starred_positions


# --- Helper methods for Munkres state machine ---

def _find_a_zero(C, row_covered, col_covered):
    n = len(C)
    for r in range(n):
        if not row_covered[r]:
            for c in range(n):
                if C[r][c] == 0 and not col_covered[c]:
                    return r, c
    return -1, -1

def _find_star_in_row(marked, row):
    n = len(marked)
    for c in range(n):
        if marked[row][c] == 1:
            return c
    return -1

def _find_star_in_col(marked, col):
    n = len(marked)
    for r in range(n):
        if marked[r][col] == 1:
            return r
    return -1

def _find_prime_in_row(marked, row):
    n = len(marked)
    for c in range(n):
        if marked[row][c] == 2:
            return c
    return -1

def _find_smallest_uncovered(C, row_covered, col_covered):
    n = len(C)
    min_val = float('inf')
    for r in range(n):
        if not row_covered[r]:
            for c in range(n):
                if not col_covered[c]:
                    if C[r][c] < min_val:
                        min_val = C[r][c]
    return min_val

def build_cost_matrix(employees: list, tasks, score_function) -> list:
    """
    Build a cost matrix where matrix[task_i][emp_i] represents
    the cost of assigning tasks[task_i] to employees[emp_i].
    Cost = 100 - Score.
    """
    if isinstance(tasks, dict):
        tasks_list = []
        for task_id, task_info in tasks.items():
            t_copy = dict(task_info)
            t_copy["id"] = task_id
            tasks_list.append(t_copy)
        tasks = tasks_list

    matrix = []
    for task in tasks:
        row = []
        for emp in employees:
            score = score_function(emp, task)
            cost = 100 - score
            row.append(cost)
        matrix.append(row)
    return matrix

def assign_tasks(employees: list, tasks, score_function) -> list:
    """
    Solve the Linear Assignment Problem by mapping employees to tasks.
    Minimizes the sum of cost (maximizes sum of suitability score).
    """
    if isinstance(tasks, dict):
        tasks_list = []
        for task_id, task_info in tasks.items():
            t_copy = dict(task_info)
            t_copy["id"] = task_id
            tasks_list.append(t_copy)
        tasks = tasks_list

    matrix = build_cost_matrix(employees, tasks, score_function)
    
    # linear_sum_assignment finds rows and cols indices
    row_idx, col_idx = linear_sum_assignment(matrix)
    
    assignments = []
    for task_i, emp_i in zip(row_idx, col_idx):
        assignments.append({
            "task": tasks[task_i]["id"],
            "employee": employees[emp_i]["name"],
            "cost": matrix[task_i][emp_i]
        })
    return assignments
