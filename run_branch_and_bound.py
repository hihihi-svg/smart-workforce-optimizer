import sys
from algorithms.branch_and_bound import branch_and_bound

# Access the module from sys.modules to read modified global states
bb_module = sys.modules['algorithms.branch_and_bound']

cost_matrix = [
    [10, 20, 30],
    [15, 8, 25],
    [18, 16, 5]
]

print("=" * 55)
print("Running Branch and Bound Assignment Validation")
print("=" * 55)

branch_and_bound(cost_matrix)

print(f"Best Cost = {bb_module.best_cost}")
print(f"Assignment: {bb_module.best_assignment}")
print(f"Nodes Pruned: {bb_module.nodes_pruned}")
print("=" * 55)
