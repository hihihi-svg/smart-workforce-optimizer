from algorithms import critical_path

# Sample tasks with durations and dependencies
tasks = {
    "T1": {"duration": 2, "deps": []},
    "T2": {"duration": 5, "deps": []},
    "T3": {"duration": 3, "deps": ["T1", "T2"]},
    "T4": {"duration": 2, "deps": ["T3"]}
}

topo = ['T1', 'T2', 'T3', 'T4']

print("=" * 50)
print("Running Critical Path Method (CPM)")
print("=" * 50)

ef, duration, critical = critical_path(tasks, topo)

print("Earliest Finish:")
for task, finish in ef.items():
    print(f"  {task} = {finish}")

print(f"\nProject Duration = {duration}")

print("\nCritical Tasks:")
print(critical)
print("=" * 50)
