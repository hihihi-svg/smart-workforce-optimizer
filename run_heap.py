from algorithms import top_k_candidates, calculate_score

employees = [
    {
        "name": "Ramesh",
        "skills": ["Python", "ML"],
        "experience": 5,
        "workload": 60
    },
    {
        "name": "Suresh",
        "skills": ["Python"],
        "experience": 2,
        "workload": 20
    },
    {
        "name": "Mahesh",
        "skills": ["Python", "ML"],
        "experience": 6,
        "workload": 30
    },
    {
        "name": "Kiran",
        "skills": ["ML"],
        "experience": 4,
        "workload": 10
    }
]

task = {
    "required_skills": ["Python", "ML"],
    "duration": 5
}

print("=" * 50)
print("Running Heap Top-K Candidates Selection")
print("=" * 50)
print(f"Selecting top 3 candidates for task with duration {task['duration']}...")

top = top_k_candidates(employees, task, 3, calculate_score)

print("\nResult (sorted by score descending):")
for score, name in top:
    print(f"  ({score}, '{name}')")

print("=" * 50)
