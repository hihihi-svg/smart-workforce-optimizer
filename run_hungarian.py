from algorithms import assign_tasks, calculate_score

# Complete test data (with all properties to prevent KeyError)
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
    }
]

tasks = [
    {
        "id": "T1",
        "required_skills": ["Python", "ML"],
        "duration": 5
    },
    {
        "id": "T2",
        "required_skills": ["Python", "ML"],
        "duration": 5
    },
    {
        "id": "T3",
        "required_skills": ["Python", "ML"],
        "duration": 5
    }
]

print("=" * 55)
print("Running Hungarian Assignment Engine (scipy)")
print("=" * 55)

result = assign_tasks(employees, tasks, calculate_score)

print("Resulting Task-to-Employee Assignments:")
for assignment in result:
    task_id = assignment["task"]
    emp_name = assignment["employee"]
    cost = assignment["cost"]
    score = 100 - cost
    print(f"  {task_id} -> {emp_name:<10} (Cost: {cost:.1f}, Suitability Score: {score:.1f}%)")

print("=" * 55)
