from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


def clean_text(text):
    """Basic text cleaning for better matching."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def calculate_match_score(resume_text, jd_text):
    """
    Calculates similarity between resume and job description
    using TF-IDF + Cosine Similarity.
    Returns a percentage score (0-100).
    """
    clean_resume = clean_text(resume_text)
    clean_jd = clean_text(jd_text)

    if not clean_resume or not clean_jd:
        return 0.0

    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform([clean_resume, clean_jd])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        score = round(float(similarity[0][0]) * 100, 2)
        return score
    except ValueError:
        return 0.0


def find_missing_skills(resume_skills, jd_text):
    """
    Compares resume skills against skills mentioned in the JD,
    returns skills present in JD but missing from resume.
    """
    jd_lower = jd_text.lower()
    missing = []
    for skill in resume_skills:
        pass  # placeholder, real logic below uses jd-extracted skills

    return missing


def get_skill_gap(resume_skills, jd_skills):
    """
    resume_skills and jd_skills are both lists.
    Returns skills in jd_skills but not in resume_skills.
    """
    resume_set = set(s.lower() for s in resume_skills)
    jd_set = set(s.lower() for s in jd_skills)
    missing = jd_set - resume_set
    matched = jd_set & resume_set
    return {
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing)
    }


def rank_resumes(resume_list, jd_text):
    """
    resume_list: list of dicts with keys 'name' and 'text'
    Returns list sorted by match score (highest first).
    """
    results = []
    for resume in resume_list:
        score = calculate_match_score(resume['text'], jd_text)
        results.append({
            "name": resume['name'],
            "score": score
        })
    results.sort(key=lambda x: x['score'], reverse=True)
    return results