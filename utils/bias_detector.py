import re


def detect_bias_elements(resume_text):
    """
    Detects potentially bias-causing information in resume.
    Returns detected elements and a cleaned version.
    """
    detected = {}
    cleaned_text = resume_text

    # 1. Detect Names (first line usually has name)
    lines = resume_text.strip().split('\n')
    first_line = lines[0].strip() if lines else ""
    if first_line and len(first_line.split()) <= 4 and first_line.replace(' ', '').isalpha():
        detected['name'] = first_line
        cleaned_text = cleaned_text.replace(first_line, '[NAME HIDDEN]', 1)

    # 2. Detect Gender indicators
    gender_patterns = {
        r'\b(Mr\.?|Mrs\.?|Ms\.?|Miss|Sir)\b': '[TITLE HIDDEN]',
        r'\b(he|his|him)\b': '[PRONOUN]',
        r'\b(she|her|hers)\b': '[PRONOUN]',
        r'\b(male|female|gender)\b': '[GENDER HIDDEN]',
    }
    gender_found = []
    for pattern, replacement in gender_patterns.items():
        matches = re.findall(pattern, resume_text, re.IGNORECASE)
        if matches:
            gender_found.extend(matches)
            cleaned_text = re.sub(pattern, replacement, cleaned_text, flags=re.IGNORECASE)
    if gender_found:
        detected['gender_indicators'] = list(set(gender_found))

    # 3. Detect Age / Date of Birth
    dob_patterns = [
        r'\b(DOB|Date of Birth|Born|Age)\s*:?\s*\d+',
        r'\b(19|20)\d{2}\s*[-–]\s*(present|current|now|19|20)\d*',
        r'\bage\s*:?\s*\d+\b',
        r'\b\d{1,2}[/-]\d{1,2}[/-](19|20)\d{2}\b',
    ]
    age_found = []
    for pattern in dob_patterns:
        matches = re.findall(pattern, resume_text, re.IGNORECASE)
        if matches:
            age_found.extend([str(m) for m in matches])
            cleaned_text = re.sub(pattern, '[AGE/DOB HIDDEN]', cleaned_text, flags=re.IGNORECASE)
    if age_found:
        detected['age_dob'] = age_found[:3]

    # 4. Detect Photo mention
    photo_patterns = r'\b(photo|photograph|picture|image|attached photo)\b'
    if re.search(photo_patterns, resume_text, re.IGNORECASE):
        detected['photo'] = ['Photo mention found']
        cleaned_text = re.sub(photo_patterns, '[PHOTO HIDDEN]', cleaned_text, flags=re.IGNORECASE)

    # 5. Detect Marital Status
    marital_patterns = r'\b(married|unmarried|single|divorced|widow|spouse|children|kids)\b'
    marital_found = re.findall(marital_patterns, resume_text, re.IGNORECASE)
    if marital_found:
        detected['marital_status'] = list(set(marital_found))
        cleaned_text = re.sub(marital_patterns, '[MARITAL STATUS HIDDEN]', cleaned_text, flags=re.IGNORECASE)

    # 6. Detect Religion
    religion_patterns = r'\b(hindu|muslim|christian|sikh|buddhist|jain|church|temple|mosque|gurudwara)\b'
    religion_found = re.findall(religion_patterns, resume_text, re.IGNORECASE)
    if religion_found:
        detected['religion'] = list(set(religion_found))
        cleaned_text = re.sub(religion_patterns, '[RELIGION HIDDEN]', cleaned_text, flags=re.IGNORECASE)

    # 7. Detect Nationality/Caste
    nationality_patterns = r'\b(nationality|caste|category|general|obc|sc|st)\b'
    nationality_found = re.findall(nationality_patterns, resume_text, re.IGNORECASE)
    if nationality_found:
        detected['nationality_caste'] = list(set(nationality_found))
        cleaned_text = re.sub(nationality_patterns, '[CATEGORY HIDDEN]', cleaned_text, flags=re.IGNORECASE)

    # Calculate bias risk score
    bias_count = len(detected)
    if bias_count == 0:
        bias_risk = "Low"
        bias_score = 95
    elif bias_count <= 2:
        bias_risk = "Medium"
        bias_score = 70
    elif bias_count <= 4:
        bias_risk = "High"
        bias_score = 45
    else:
        bias_risk = "Very High"
        bias_score = 20

    return {
        "detected": detected,
        "cleaned_text": cleaned_text,
        "bias_risk": bias_risk,
        "bias_score": bias_score,
        "total_bias_elements": bias_count,
        "is_bias_free": bias_count == 0
    }