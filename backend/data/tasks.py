tasks = {
    "T1": {
        "required_skills": ['ML', 'Kubernetes', 'Node'],
        "duration": 6,
        "deps": []
    },
    "T2": {
        "required_skills": ['Data Science', 'Docker'],
        "duration": 5,
        "deps": ['T1']
    },
    "T3": {
        "required_skills": ['Kubernetes', 'HTML', 'Spring Boot'],
        "duration": 4,
        "deps": ['T1', 'T2']
    },
    "T4": {
        "required_skills": ['ML', 'Linux', 'Figma'],
        "duration": 4,
        "deps": []
    },
    "T5": {
        "required_skills": ['DevOps'],
        "duration": 2,
        "deps": ['T4']
    },
    "T6": {
        "required_skills": ['ML'],
        "duration": 4,
        "deps": []
    },
    "T7": {
        "required_skills": ['Linux', 'QA', 'Docker'],
        "duration": 4,
        "deps": []
    },
    "T8": {
        "required_skills": ['QA', 'CSS', 'UI/UX'],
        "duration": 4,
        "deps": ['T5']
    },
    "T9": {
        "required_skills": ['C++', 'Linux', 'SQL'],
        "duration": 3,
        "deps": []
    },
    "T10": {
        "required_skills": ['Docker', 'Data Science', 'UI/UX'],
        "duration": 4,
        "deps": []
    },
    "T11": {
        "required_skills": ['PyTorch', 'React'],
        "duration": 7,
        "deps": ['T10', 'T9']
    },
    "T12": {
        "required_skills": ['Linux', 'Kubernetes'],
        "duration": 5,
        "deps": []
    },
    "T13": {
        "required_skills": ['Python', 'Kubernetes', 'SQL'],
        "duration": 5,
        "deps": []
    },
    "T14": {
        "required_skills": ['QA', 'DevOps', 'UI/UX'],
        "duration": 3,
        "deps": ['T1', 'T10']
    },
    "T15": {
        "required_skills": ['Selenium', 'Node'],
        "duration": 3,
        "deps": ['T5']
    },
    "T16": {
        "required_skills": ['AWS', 'Selenium', 'Java'],
        "duration": 3,
        "deps": ['T6', 'T8']
    },
    "T17": {
        "required_skills": ['Python', 'QA'],
        "duration": 5,
        "deps": []
    },
    "T18": {
        "required_skills": ['Java', 'React'],
        "duration": 3,
        "deps": ['T13']
    },
    "T19": {
        "required_skills": ['Docker'],
        "duration": 6,
        "deps": []
    },
    "T20": {
        "required_skills": ['PyTorch', 'Spring Boot'],
        "duration": 4,
        "deps": ['T1', 'T18']
    },
}
