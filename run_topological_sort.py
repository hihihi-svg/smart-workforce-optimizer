from algorithms import topological_sort

# Sample tasks with dependencies (predecessors)
tasks = {
    "T1": [],
    "T2": [],
    "T3": ["T1", "T2"],
    "T4": ["T3"],
    "T5": ["T2"]
}

print("=" * 50)
print("Running Topological Sort (Kahn's Algorithm)")
print("=" * 50)
print("Input Task Dependencies (predecessors):")
for task, deps in tasks.items():
    print(f"  {task:<4} depends on: {deps}")

print("\nRunning topological_sort(tasks)...")
result = topological_sort(tasks)

print("\nResulting Order:")
print(result)

# Test cycle detection
print("\n" + "-" * 50)
print("Testing Cycle Detection:")
cyclic_tasks = {
    "Task_A": ["Task_B"],
    "Task_B": ["Task_C"],
    "Task_C": ["Task_A"]
}
print("Input Cyclic Dependencies:")
for task, deps in cyclic_tasks.items():
    print(f"  {task:<6} depends on: {deps}")

cyclic_result = topological_sort(cyclic_tasks)
print(f"Result for cycle: {cyclic_result}")
print("=" * 50)
