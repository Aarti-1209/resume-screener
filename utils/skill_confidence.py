import re


def calculate_skill_confidence(resume_text, skills):
    """
    Calculates confidence score for each skill based on
    how many times and how strongly it appears in the resume.
    Returns list of dicts with skill name and confidence (0-100).
    """
    text_lower = resume_text.lower()
    word_count = len(resume_text.split())
    results = []

    for skill in skills:
        skill_lower = skill.lower()
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        matches = re.findall(pattern, text_lower)
        count = len(matches)

        if count == 0:
            continue

        # Base score from frequency
        frequency_score = min(count * 20, 60)

        # Bonus if mentioned in first 30% of resume (summary/headline area)
        first_part = text_lower[:int(len(text_lower) * 0.3)]
        if re.search(pattern, first_part):
            frequency_score += 20

        # Bonus for context words nearby
        context_bonus = 0
        context_words = ['expert', 'proficient', 'experienced', 'advanced',
                        'strong', 'years', 'project', 'built', 'developed',
                        'implemented', 'worked', 'used', 'knowledge']
        for word in context_words:
            if word in text_lower:
                context_bonus += 2

        final_score = min(frequency_score + min(context_bonus, 20), 100)

        results.append({
            "skill": skill,
            "confidence": final_score,
            "count": count,
            "level": "Expert" if final_score >= 80 else
                     "Proficient" if final_score >= 60 else
                     "Familiar" if final_score >= 40 else "Basic"
        })

    results.sort(key=lambda x: x['confidence'], reverse=True)
    return results