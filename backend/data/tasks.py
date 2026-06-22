tasks = {
    # ── No dependencies (start nodes) ───────────────────────────────
    "T1": {
        "name": "ML Model Training",
        "required_skills": ["ML", "Python"],
        "duration": 6,
        "deps": []
    },
    "T2": {
        "name": "Backend API Development",
        "required_skills": ["Python", "SQL", "Node"],
        "duration": 5,
        "deps": []
    },
    "T3": {
        "name": "Frontend UI Build",
        "required_skills": ["React", "TypeScript", "CSS"],
        "duration": 4,
        "deps": []
    },
    "T4": {
        "name": "Infrastructure Setup",
        "required_skills": ["Docker", "Kubernetes", "Linux"],
        "duration": 3,
        "deps": []
    },
    "T5": {
        "name": "Data Pipeline",
        "required_skills": ["Data Science", "Python", "SQL"],
        "duration": 4,
        "deps": []
    },

    # ── Depend on earlier tasks ──────────────────────────────────────
    "T6": {
        "name": "Model Evaluation & Tuning",
        "required_skills": ["ML", "PyTorch", "Python"],
        "duration": 5,
        "deps": ["T1", "T5"]
    },
    "T7": {
        "name": "API Integration & Testing",
        "required_skills": ["QA", "Selenium", "Node"],
        "duration": 3,
        "deps": ["T2", "T3"]
    },
    "T8": {
        "name": "Cloud Deployment",
        "required_skills": ["AWS", "Docker", "DevOps"],
        "duration": 4,
        "deps": ["T4", "T7"]
    },
    "T9": {
        "name": "UI/UX Polish & Accessibility",
        "required_skills": ["Figma", "React", "UI/UX"],
        "duration": 3,
        "deps": ["T3"]
    },

    # ── Final integration ────────────────────────────────────────────
    "T10": {
        "name": "End-to-End QA & Sign-off",
        "required_skills": ["QA", "Testing", "Selenium"],
        "duration": 4,
        "deps": ["T6", "T8", "T9"]
    },
}
