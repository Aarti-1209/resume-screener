import re
from datetime import datetime


def detect_fake_resume(resume_text):
    """
    Detects potential red flags in a resume that might indicate
    fake or inflated information.
    """
    red_flags = []
    warnings = []
    score = 100  # Start with perfect score, deduct for issues

    text_lower = resume_text.lower()
    lines = resume_text.strip().split('\n')

    # 1. Check for date overlaps (working two full-time jobs simultaneously)
    years = re.findall(r'\b(20\d{2})\b', resume_text)
    years = [int(y) for y in years]
    if len(years) >= 4:
        years_sorted = sorted(years)
        # Check if too many overlapping periods
        unique_years = list(set(years))
        if len(years) - len(unique_years) > 3:
            red_flags.append({
                "type": "Date Overlap",
                "detail": "Multiple overlapping date ranges detected — possible timeline inconsistency.",
                "severity": "High"
            })
            score -= 25

    # 2. Check for keyword stuffing
    skill_keywords = [
        "python", "java", "javascript", "machine learning", "deep learning",
        "tensorflow", "pytorch", "docker", "kubernetes", "aws", "azure",
        "react", "angular", "node", "sql", "mongodb", "flask", "django"
    ]
    skill_count = sum(1 for skill in skill_keywords if skill in text_lower)
    word_count = len(resume_text.split())

    if word_count > 0:
        skill_density = skill_count / (word_count / 100)
        if skill_density > 8:
            red_flags.append({
                "type": "Keyword Stuffing",
                "detail": f"Unusually high skill density detected ({skill_count} tech skills in {word_count} words). Resume may be keyword-stuffed to game ATS systems.",
                "severity": "Medium"
            })
            score -= 20

    # 3. Check for too many buzzwords
    buzzwords = [
        "synergy", "leverage", "paradigm", "disruptive", "innovative",
        "thought leader", "guru", "ninja", "rockstar", "wizard",
        "passionate", "dynamic", "results-driven", "self-starter",
        "team player", "detail-oriented", "go-getter", "visionary"
    ]
    buzzword_count = sum(1 for bw in buzzwords if bw in text_lower)
    if buzzword_count >= 4:
        warnings.append({
            "type": "Excessive Buzzwords",
            "detail": f"Found {buzzword_count} generic buzzwords. Strong resumes use specific achievements, not vague descriptors.",
            "severity": "Low"
        })
        score -= 10

    # 4. Check for unrealistic claims
    unrealistic_patterns = [
        (r'\b(expert|master|guru)\s+in\s+\d+\+?\s*(languages|frameworks|tools)', "Claims mastery in too many technologies"),
        (r'\b(\d{2,})\s*\+?\s*years\s+of\s+experience\b', "Claimed experience years seem unusually high"),
        (r'increased\s+\w+\s+by\s+(\d{3,})\s*%', "Percentage improvement claims seem unrealistic"),
    ]
    for pattern, message in unrealistic_patterns:
        match = re.search(pattern, text_lower)
        if match:
            warnings.append({
                "type": "Unrealistic Claim",
                "detail": message,
                "severity": "Medium"
            })
            score -= 10

    # 5. Check for missing key sections
    required_sections = {
        "experience": ["experience", "work history", "employment"],
        "education": ["education", "degree", "university", "college"],
        "contact": ["email", "phone", "contact"]
    }
    missing_sections = []
    for section, keywords in required_sections.items():
        if not any(kw in text_lower for kw in keywords):
            missing_sections.append(section)

    if missing_sections:
        red_flags.append({
            "type": "Missing Sections",
            "detail": f"Key sections missing: {', '.join(missing_sections)}. A complete resume should have contact info, education, and experience.",
            "severity": "High"
        })
        score -= 20

    # 6. Check for copy-paste indicators
    if resume_text.count('  ') > 20:
        warnings.append({
            "type": "Formatting Issues",
            "detail": "Excessive whitespace detected — may indicate copy-paste from multiple sources.",
            "severity": "Low"
        })
        score -= 5

    # 7. Check for generic job descriptions
    generic_phrases = [
        "responsible for", "duties included", "helped with",
        "assisted in", "worked on", "participated in"
    ]
    generic_count = sum(1 for phrase in generic_phrases if phrase in text_lower)
    if generic_count >= 3:
        warnings.append({
            "type": "Weak Action Words",
            "detail": f"Found {generic_count} weak/passive phrases. Use strong action verbs like 'built', 'developed', 'led', 'achieved'.",
            "severity": "Low"
        })
        score -= 5

    # Final assessment
    score = max(0, min(100, score))

    if len(red_flags) == 0 and len(warnings) == 0:
        verdict = "Looks Authentic"
        verdict_color = "green"
    elif len(red_flags) == 0:
        verdict = "Minor Concerns"
        verdict_color = "orange"
    elif len(red_flags) <= 2:
        verdict = "Suspicious"
        verdict_color = "red"
    else:
        verdict = "High Risk"
        verdict_color = "darkred"

    return {
        "authenticity_score": score,
        "verdict": verdict,
        "verdict_color": verdict_color,
        "red_flags": red_flags,
        "warnings": warnings,
        "total_issues": len(red_flags) + len(warnings)
    }