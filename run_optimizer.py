import sys
from algorithms import (
    generate_suitability_matrix,
    solve_hungarian,
    greedy_assignment,
)

def print_header(title):
    print("\n" + "=" * 60)
    print(f" {title} ".center(60, "="))
    print("=" * 60)

def get_input_choice(prompt, options):
    while True:
        val = input(prompt).strip().lower()
        if val in options:
            return val
        print(f"Invalid option. Please choose from {options}")

def load_sample_data():
    employees = [
        {"name": "Alice (Frontend Developer)", "skills": {"React": 5, "CSS": 4, "Git": 3}, "hourly_rate": 55, "availability": 1.0},
        {"name": "Bob (Backend Engineer)", "skills": {"Python": 5, "SQL": 4, "Docker": 3}, "hourly_rate": 60, "availability": 0.8},
        {"name": "Charlie (Fullstack Dev)", "skills": {"React": 4, "Python": 3, "SQL": 3}, "hourly_rate": 65, "availability": 0.9},
        {"name": "Diana (UI/UX Designer)", "skills": {"Figma": 5, "CSS": 3}, "hourly_rate": 45, "availability": 1.0},
    ]

    tasks = [
        {"name": "Build Login Page UI", "required_skills": {"React": 4, "CSS": 3}, "budget_rate": 50},
        {"name": "Setup Database Schema", "required_skills": {"SQL": 4, "Python": 3}, "budget_rate": 60},
        {"name": "Design Logo & Brand", "required_skills": {"Figma": 4}, "budget_rate": 50},
    ]
    return employees, tasks

def input_manual_data():
    employees = []
    tasks = []
    
    print("\n--- Enter Employees ---")
    try:
        num_emp = int(input("How many employees? ").strip())
    except ValueError:
        print("Invalid number. Defaulting to 0.")
        num_emp = 0

    for i in range(num_emp):
        print(f"\nEmployee #{i + 1}:")
        name = input("  Name/Role: ").strip() or f"Employee {i+1}"
        
        skills = {}
        print("  Enter skills (e.g. 'Python:5, SQL:4'). Press enter when done.")
        skills_raw = input("  Skills: ").strip()
        if skills_raw:
            for part in skills_raw.split(","):
                if ":" in part:
                    s_name, s_lvl = part.split(":", 1)
                    try:
                        skills[s_name.strip()] = int(s_lvl.strip())
                    except ValueError:
                        skills[s_name.strip()] = 3
                else:
                    skills[part.strip()] = 3
                    
        try:
            rate = float(input("  Hourly Rate ($): ").strip())
        except ValueError:
            rate = 50.0
            
        try:
            avail = float(input("  Availability (0.0 to 1.0): ").strip())
        except ValueError:
            avail = 1.0
            
        employees.append({
            "name": name,
            "skills": skills,
            "hourly_rate": rate,
            "availability": avail
        })

    print("\n--- Enter Tasks ---")
    try:
        num_tasks = int(input("How many tasks? ").strip())
    except ValueError:
        print("Invalid number. Defaulting to 0.")
        num_tasks = 0

    for i in range(num_tasks):
        print(f"\nTask #{i + 1}:")
        name = input("  Task Name: ").strip() or f"Task {i+1}"
        
        req_skills = {}
        print("  Required skills & levels (e.g. 'Python:4, SQL:3'). Press enter when done.")
        skills_raw = input("  Required Skills: ").strip()
        if skills_raw:
            for part in skills_raw.split(","):
                if ":" in part:
                    s_name, s_lvl = part.split(":", 1)
                    try:
                        req_skills[s_name.strip()] = int(s_lvl.strip())
                    except ValueError:
                        req_skills[s_name.strip()] = 3
                else:
                    req_skills[part.strip()] = 3
                    
        try:
            budget = float(input("  Budget Target Rate ($): ").strip())
        except ValueError:
            budget = 60.0

        tasks.append({
            "name": name,
            "required_skills": req_skills,
            "budget_rate": budget
        })
        
    return employees, tasks

def main():
    print_header("Smart Workforce Optimizer CLI")
    print("This utility matches employees to tasks optimally using DAA algorithms.")
    
    choice = get_input_choice(
        "Would you like to (s)tart with sample data or (m)anually input data? [s/m]: ",
        ['s', 'm', 'sample', 'manual']
    )
    
    if choice in ['s', 'sample']:
        employees, tasks = load_sample_data()
    else:
        employees, tasks = input_manual_data()

    if not employees or not tasks:
        print("\nError: You need at least 1 employee and 1 task to run optimization.")
        return

    # 1. Compute suitability score matrix (Higher is better)
    weights = {"skill": 0.6, "cost": 0.3, "availability": 0.1}
    matrix = generate_suitability_matrix(employees, tasks, weights)
    
    print("\n--- Suitability Scores Matrix (Employee vs Task) ---")
    # Print headers
    header_str = f"{'Employee Name':<30}"
    for t in tasks:
        header_str += f" | {t['name'][:18]:<18}"
    print(header_str)
    print("-" * len(header_str))
    
    for i, emp in enumerate(employees):
        row_str = f"{emp['name']:<30}"
        for score in matrix[i]:
            row_str += f" | {score:<18.2f}%"
        print(row_str)

    # 2. Run Hungarian (Optimal) algorithm (Maximizing suitability)
    hungarian_assignments, hungarian_total = solve_hungarian(matrix, maximize=True)
    
    # 3. Run Greedy (Heuristic) algorithm
    greedy_assignments, greedy_total = greedy_assignment(matrix, maximize=True)

    # 4. Display Hungarian Results
    print_header("Hungarian Algorithm (Optimal Assignment)")
    print(f"Total Combined Match Score: {hungarian_total:.2f}% (Average: {hungarian_total / len(hungarian_assignments):.2f}%)\n")
    for r, c in hungarian_assignments:
        emp = employees[r]
        tsk = tasks[c]
        score = matrix[r][c]
        print(f"  * Assign: {emp['name']:<30} -> {tsk['name']:<25} (Suitability: {score:.2f}%)")

    # 5. Display Greedy Results
    print_header("Greedy Algorithm (Heuristic Assignment)")
    print(f"Total Combined Match Score: {greedy_total:.2f}% (Average: {greedy_total / len(greedy_assignments):.2f}%)\n")
    for r, c in greedy_assignments:
        emp = employees[r]
        tsk = tasks[c]
        score = matrix[r][c]
        print(f"  * Assign: {emp['name']:<30} -> {tsk['name']:<25} (Suitability: {score:.2f}%)")

    # 6. Compare Efficiency
    print_header("Comparison Analysis")
    diff = hungarian_total - greedy_total
    print(f"Hungarian Total Match Score : {hungarian_total:.2f}%")
    print(f"Greedy Total Match Score    : {greedy_total:.2f}%")
    if diff > 0:
        print(f"[*] The Hungarian Algorithm found a better assignment by {diff:.2f}%.")
    else:
        print("[*] The Greedy heuristic managed to match the optimal Hungarian matching.")

if __name__ == "__main__":
    main()
