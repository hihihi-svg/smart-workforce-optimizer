from algorithms import calculate_score

# Test dataset
task = {
    "required_skills": ["Python", "ML"],
    "duration": 5
}

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
    }
]

print("=" * 50)
print("Running Employee Scoring Function")
print("=" * 50)
print("Target Task:")
print(f"  Required Skills: {task['required_skills']}")
print(f"  Duration: {task['duration']} days")
print("-" * 50)

for emp in employees:
    score = calculate_score(emp, task)
    print(f"Employee: {emp['name']:<10} | Score: {score}")

print("=" * 50)
