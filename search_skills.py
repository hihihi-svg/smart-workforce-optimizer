import sys
from algorithms import Trie

def load_sample_employees():
    return [
        {"name": "Alice", "title": "Frontend Developer", "skills": {"React": 5, "CSS": 4, "Git": 3, "HTML": 5}},
        {"name": "Bob", "title": "Backend Engineer", "skills": {"Python": 5, "SQL": 4, "Docker": 3, "PostgreSQL": 4}},
        {"name": "Charlie", "title": "Fullstack Developer", "skills": {"React": 4, "Python": 3, "SQL": 3, "JavaScript": 5}},
        {"name": "Diana", "title": "UI/UX Designer", "skills": {"Figma": 5, "CSS": 3, "Illustrator": 4}},
        {"name": "Evan", "title": "DevOps Engineer", "skills": {"Docker": 5, "Kubernetes": 4, "AWS": 4, "Git": 4}},
        {"name": "Frank", "title": "QA Engineer", "skills": {"Python": 3, "Selenium": 5, "Git": 3}},
    ]

def main():
    print("=" * 65)
    print(" " * 15 + "Employee Skill Prefix Search (Trie-Based)")
    print("=" * 65)
    print("Initializing Trie Index...")
    
    employees = load_sample_employees()
    trie = Trie()
    
    # Index all employee skills in the Trie
    for emp in employees:
        for skill_name, level in emp["skills"].items():
            # Associate employee data with the skill name in the Trie
            data = {
                "employee_name": emp["name"],
                "title": emp["title"],
                "level": level
            }
            trie.insert(skill_name, data)
            
    print("Trie populated successfully!")
    print("Available skills in database: React, CSS, Git, HTML, Python, SQL, Docker, PostgreSQL, JavaScript, Figma, Illustrator, Kubernetes, AWS, Selenium")
    print("-" * 65)
    print("Type a skill prefix to search (e.g. 'py', 'do', 'gi').")
    print("Type 'exit' or 'quit' to close the utility.")
    print("-" * 65)
    
    while True:
        try:
            prefix = input("\nEnter skill prefix: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting search utility...")
            break
            
        if not prefix:
            continue
            
        if prefix.lower() in ["exit", "quit"]:
            print("Exiting search utility...")
            break
            
        results = trie.starts_with(prefix)
        
        if not results:
            print(f"[-] No skills found starting with '{prefix}'.")
            continue
            
        print(f"\n[+] Found {len(results)} matching skill(s):")
        for match in results:
            skill = match["word"]
            associated_employees = match["data"]
            
            print(f"\nSkill: {skill}")
            print(f"  {'Employee Name':<15} | {'Job Title':<25} | {'Level (1-5)':<12}")
            print(f"  {'-'*15}-|-{'-'*25}-|-{'-'*12}")
            
            # Sort employees by skill level descending
            sorted_emps = sorted(associated_employees, key=lambda x: x["level"], reverse=True)
            for emp_info in sorted_emps:
                print(f"  {emp_info['employee_name']:<15} | {emp_info['title']:<25} | {emp_info['level']:<12}")
            print()

if __name__ == "__main__":
    main()
