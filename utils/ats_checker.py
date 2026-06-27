import re


def check_ats_compatibility(resume_text):
    """
    Checks resume text for ATS compatibility issues.
    Returns a score and list of issues/suggestions.
    """
    issues = []
    passed = []
    score = 100

    # 1. Check length
    word_count = len(resume_text.split())
    if word_count < 200:
        issues.append("Resume is too short — ATS systems prefer 400-800 words.")
        score -= 15
    elif word_count > 1200:
        issues.append("Resume may be too long — keep it under 1000 words ideally.")
        score -= 5
    else:
        passed.append("Good resume length detected.")

    # 2. Check for contact info
    has_email = bool(re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resume_text))
    has_phone = bool(re.search(r'(\+?\d[\d\s\-().]{7,}\d)', resume_text))

    if not has_email:
        issues.append("No email address detected — ATS needs contact information.")
        score -= 15
    else:
        passed.append("Email address found.")

    if not has_phone:
        issues.append("No phone number detected — add your contact number.")
        score -= 10
    else:
        passed.append("Phone number found.")

    # 3. Check for common sections
    text_lower = resume_text.lower()
    sections = {
        "experience": ["experience", "work history", "employment", "internship"],
        "education": ["education", "academic", "degree", "university", "college"],
        "skills": ["skills", "technical skills", "core competencies", "expertise"],
    }

    for section, keywords in sections.items():
        if any(kw in text_lower for kw in keywords):
            passed.append(f"{section.capitalize()} section detected.")
        else:
            issues.append(f"No {section} section found — ATS looks for standard section headings.")
            score -= 10

    # 4. Check for dates
    has_dates = bool(re.search(r'\b(19|20)\d{2}\b', resume_text))
    if not has_dates:
        issues.append("No dates found — add years to your experience and education.")
        score -= 10
    else:
        passed.append("Dates found in resume.")

    # 5. Check for keywords density
    if word_count > 0:
        unique_words = len(set(resume_text.lower().split()))
        diversity = unique_words / word_count
        if diversity < 0.4:
            issues.append("Possible keyword stuffing detected — use varied vocabulary.")
            score -= 10
        else:
            passed.append("Good vocabulary diversity.")

    # 6. Check for special characters that confuse ATS
    special_chars = len(re.findall(r'[|•►▶◆★☆✓✗→←↑↓]', resume_text))
    if special_chars > 10:
        issues.append(f"Found {special_chars} special characters — ATS may not parse these correctly. Use simple bullet points.")
        score -= 10
    else:
        passed.append("No problematic special characters detected.")

    # 7. Check for URLs/LinkedIn
    has_linkedin = bool(re.search(r'linkedin\.com', text_lower))
    has_github = bool(re.search(r'github\.com', text_lower))
    if has_linkedin:
        passed.append("LinkedIn profile found.")
    else:
        issues.append("No LinkedIn URL found — add your LinkedIn profile.")
        score -= 5

    if has_github:
        passed.append("GitHub profile found.")

    # Final score
    score = max(0, min(100, score))

    if score >= 80:
        rating = "Excellent"
        color = "green"
    elif score >= 60:
        rating = "Good"
        color = "blue"
    elif score >= 40:
        rating = "Fair"
        color = "orange"
    else:
        rating = "Poor"
        color = "red"

    return {
        "score": score,
        "rating": rating,
        "color": color,
        "issues": issues,
        "passed": passed,
        "word_count": word_count,
    }