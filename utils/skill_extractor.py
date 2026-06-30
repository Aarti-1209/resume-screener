import re

COMMON_SKILLS = [
    "python", "java", "javascript", "c++", "c#", "sql", "html", "css",
    "react", "angular", "vue", "node.js", "django", "flask", "spring",
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
    "data analysis", "data science", "data visualization",
    "aws", "azure", "gcp", "docker", "kubernetes", "git", "github",
    "mongodb", "mysql", "postgresql", "redis", "rest api", "graphql",
    "agile", "scrum", "leadership", "communication", "teamwork",
    "project management", "problem solving", "excel", "tableau",
    "power bi", "linux", "bash", "ci/cd", "jenkins", "microservices",
    "streamlit", "fastapi", "spacy", "nltk", "opencv", "selenium",
    "testing", "automation", "cloud computing", "blockchain",
    "android", "ios", "swift", "kotlin", "r programming", "matlab",
    "spark", "hadoop", "kafka", "elasticsearch", "firebase"
]

EDUCATION_KEYWORDS = [
    "b.tech", "btech", "bachelor", "b.e.", "be", "m.tech", "mtech",
    "master", "phd", "doctorate", "mba", "bca", "mca", "diploma",
    "high school", "associate degree"
]


def extract_skills(text):
    text_lower = text.lower()
    found_skills = []
    for skill in COMMON_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    return sorted(set(found_skills))


def extract_education(text):
    text_lower = text.lower()
    found = []
    for keyword in EDUCATION_KEYWORDS:
        if keyword in text_lower:
            found.append(keyword)
    return sorted(set(found))


def extract_experience_years(text):
    patterns = [
        r'(\d+)\+?\s*years?\s*(of)?\s*experience',
        r'experience\s*(of|:)?\s*(\d+)\+?\s*years?'
    ]
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            for group in match.groups():
                if group and group.isdigit():
                    return int(group)
    return None


def extract_entities(text):
    """Lightweight name detection using regex (no spaCy needed)."""
    lines = text.strip().split('\n')
    first_line = lines[0].strip() if lines else ""
    persons = []
    if first_line and len(first_line.split()) <= 4 and first_line.replace(' ', '').isalpha():
        persons = [first_line]

    orgs = re.findall(r'\b[A-Z][a-zA-Z]*\s+(?:Inc|Ltd|LLC|Corp|Technologies|Solutions|Systems)\b', text)

    return {"PERSON": persons, "ORG": orgs[:5], "GPE": []}


def analyze_resume(text):
    return {
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience_years": extract_experience_years(text),
        "entities": extract_entities(text)
    }