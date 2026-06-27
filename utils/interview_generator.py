import random


SKILL_QUESTION_TEMPLATES = {
    "python": [
        "Can you explain the difference between a list and a tuple in Python?",
        "How do you handle exceptions in Python? Walk me through a real example.",
        "What are Python decorators and when have you used them?",
    ],
    "machine learning": [
        "Walk me through how you would approach a classification problem from scratch.",
        "How do you handle overfitting in a machine learning model?",
        "Explain the difference between supervised and unsupervised learning with an example from your work.",
    ],
    "deep learning": [
        "Can you explain how backpropagation works in a neural network?",
        "What's the difference between CNN and RNN architectures, and when would you use each?",
    ],
    "nlp": [
        "How would you approach building a text classification system?",
        "Can you explain the concept of word embeddings and why they're useful?",
    ],
    "tensorflow": [
        "Describe a project where you used TensorFlow. What challenges did you face?",
    ],
    "pytorch": [
        "Describe a project where you used PyTorch. What challenges did you face?",
    ],
    "sql": [
        "Write a SQL query to find duplicate records in a table — can you describe your approach?",
        "How do you optimize a slow-running SQL query?",
    ],
    "flask": [
        "How would you structure a Flask application for scalability?",
        "Explain how routing works in Flask.",
    ],
    "pandas": [
        "How do you handle missing data in a pandas DataFrame?",
        "Describe a time you used pandas to clean a messy dataset.",
    ],
    "git": [
        "Walk me through your typical Git workflow when working on a team project.",
        "How do you resolve a merge conflict?",
    ],
    "data analysis": [
        "Describe a data analysis project end-to-end, from raw data to insights.",
    ],
    "aws": [
        "What AWS services have you used, and for what purpose?",
    ],
    "docker": [
        "How would you containerize a Python application using Docker?",
    ],
}

BEHAVIORAL_QUESTIONS = [
    "Tell me about a time you faced a difficult challenge in a project. How did you handle it?",
    "Describe a situation where you had to learn a new technology quickly. What was your approach?",
    "How do you prioritize tasks when working on multiple projects with tight deadlines?",
    "Tell me about a time you received constructive criticism. How did you respond?",
    "Describe a time you worked in a team and faced a disagreement. How was it resolved?",
]

SCENARIO_QUESTIONS = [
    "If you joined our team tomorrow, how would you approach understanding our existing codebase?",
    "Imagine a model you built is performing well in testing but poorly in production. How would you debug this?",
    "If a stakeholder asked you to explain a technical concept to a non-technical audience, how would you do it?",
]


def generate_interview_questions(skills, education, jd_text, num_questions=8):
    questions = []

    matched_topics = [s for s in skills if s.lower() in SKILL_QUESTION_TEMPLATES]
    for topic in matched_topics:
        topic_questions = SKILL_QUESTION_TEMPLATES[topic.lower()]
        questions.append(random.choice(topic_questions))
        if len(questions) >= num_questions - 3:
            break

    remaining = num_questions - len(questions)
    behavioral_count = min(2, remaining)
    questions.extend(random.sample(BEHAVIORAL_QUESTIONS, behavioral_count))

    remaining = num_questions - len(questions)
    if remaining > 0:
        questions.extend(random.sample(SCENARIO_QUESTIONS, min(remaining, len(SCENARIO_QUESTIONS))))

    if not questions:
        questions = random.sample(BEHAVIORAL_QUESTIONS, 3) + random.sample(SCENARIO_QUESTIONS, 2)

    return {"questions": questions[:num_questions]}


def generate_improvement_tips(resume_skills, missing_skills, experience_years):
    tips = []

    if missing_skills:
        top_missing = missing_skills[:3]
        tips.append(
            f"Consider adding experience or projects involving {', '.join(top_missing)}, "
            f"as these are mentioned in the job description but missing from your resume."
        )

    if not experience_years:
        tips.append(
            "Your resume doesn't clearly state years of experience — "
            "consider adding a summary line specifying your total relevant experience."
        )

    if len(resume_skills) < 5:
        tips.append(
            "Your resume lists relatively few technical skills — "
            "consider adding more specific tools, libraries, or frameworks you've used."
        )

    tips.append(
        "Quantify your achievements with numbers where possible "
        "(e.g. 'improved model accuracy by 15%' or 'reduced processing time by 30%')."
    )

    tips.append(
        "Tailor your resume summary or objective to closely match the keywords "
        "used in this specific job description."
    )

    return {"tips": tips[:4]}