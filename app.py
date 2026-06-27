from flask import Flask, render_template, request, jsonify, Response
import os
import json
from dotenv import load_dotenv

from utils.skill_confidence import calculate_skill_confidence
from utils.bias_detector import detect_bias_elements
from utils.fake_resume_detector import detect_fake_resume
from utils.pdf_reader import extract_text_from_upload
from utils.skill_extractor import analyze_resume
from utils.matcher import calculate_match_score, get_skill_gap, rank_resumes
from utils.interview_generator import generate_interview_questions, generate_improvement_tips
from utils.ats_checker import check_ats_compatibility
from utils.pdf_report import generate_pdf_report

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    jd_text = request.form.get('job_description', '')
    resume_file = request.files.get('resume')

    if not resume_file or not jd_text.strip():
        return jsonify({"error": "Please provide both a resume and a job description."}), 400

    resume_text = extract_text_from_upload(resume_file)
    if not resume_text:
        return jsonify({"error": "Could not extract text from the uploaded PDF."}), 400

    resume_analysis = analyze_resume(resume_text)
    jd_analysis = analyze_resume(jd_text)

    ats_result = check_ats_compatibility(resume_text)
    bias_result = detect_bias_elements(resume_text)
    fake_result = detect_fake_resume(resume_text)
    skill_confidence = calculate_skill_confidence(resume_text, resume_analysis['skills'])
    match_score = calculate_match_score(resume_text, jd_text)
    skill_gap = get_skill_gap(resume_analysis['skills'], jd_analysis['skills'])

    interview_result = generate_interview_questions(
        resume_analysis['skills'], resume_analysis['education'], jd_text
    )
    tips_result = generate_improvement_tips(
        resume_analysis['skills'], skill_gap['missing_skills'],
        resume_analysis['experience_years']
    )

    return jsonify({
        "match_score": match_score,
        "skills": resume_analysis['skills'],
        "education": resume_analysis['education'],
        "experience_years": resume_analysis['experience_years'],
        "matched_skills": skill_gap['matched_skills'],
        "missing_skills": skill_gap['missing_skills'],
        "interview_questions": interview_result.get('questions', []),
        "improvement_tips": tips_result.get('tips', []),
        "interview_error": interview_result.get('error'),
        "tips_error": tips_result.get('error'),
        "ats_score": ats_result['score'],
        "ats_rating": ats_result['rating'],
        "ats_color": ats_result['color'],
        "ats_issues": ats_result['issues'],
        "ats_passed": ats_result['passed'],
        "ats_word_count": ats_result['word_count'],
        "bias_risk": bias_result['bias_risk'],
"bias_score": bias_result['bias_score'],
"bias_detected": bias_result['detected'],
"bias_elements_count": bias_result['total_bias_elements'],
"is_bias_free": bias_result['is_bias_free'],
"authenticity_score": fake_result['authenticity_score'],
"verdict": fake_result['verdict'],
"verdict_color": fake_result['verdict_color'],
"red_flags": fake_result['red_flags'],
"warnings": fake_result['warnings'],
"total_issues": fake_result['total_issues'],
        "skill_confidence": skill_confidence,
    })


@app.route('/analyze-jd', methods=['POST'])
def analyze_jd():
    jd_text = request.form.get('job_description', '')

    if not jd_text.strip():
        return jsonify({"error": "Please provide a job description."}), 400

    jd_analysis = analyze_resume(jd_text)
    interview_result = generate_interview_questions(
        jd_analysis['skills'], [], jd_text, num_questions=8
    )
    tips_result = generate_improvement_tips(
        [], jd_analysis['skills'], None
    )

    level = "Entry Level"
    jd_lower = jd_text.lower()
    if any(w in jd_lower for w in ['senior', 'lead', 'principal', '5+ years', '7+ years']):
        level = "Senior Level"
    elif any(w in jd_lower for w in ['mid', 'intermediate', '2+ years', '3+ years', '4+ years']):
        level = "Mid Level"

    competition = "Medium"
    if len(jd_analysis['skills']) > 10:
        competition = "High — Many skills required"
    elif len(jd_analysis['skills']) < 5:
        competition = "Low — Few specific requirements"

    return jsonify({
        "required_skills": jd_analysis['skills'],
        "education_required": jd_analysis['education'],
        "experience_level": level,
        "competition": competition,
        "interview_questions": interview_result.get('questions', []),
        "ideal_profile": tips_result.get('tips', []),
        "total_skills": len(jd_analysis['skills'])
    })


@app.route('/rank', methods=['POST'])
def rank():
    jd_text = request.form.get('job_description', '')
    resume_files = request.files.getlist('resumes')

    if not resume_files or not jd_text.strip():
        return jsonify({"error": "Please provide resumes and a job description."}), 400

    resume_list = []
    for file in resume_files:
        text = extract_text_from_upload(file)
        if text:
            resume_list.append({"name": file.filename, "text": text})

    if not resume_list:
        return jsonify({"error": "Could not extract text from any uploaded resumes."}), 400

    ranked = rank_resumes(resume_list, jd_text)
    return jsonify({"ranked_resumes": ranked})


@app.route('/download-report', methods=['POST'])
def download_report():
    data = request.form.get('report_data', '{}')
    report_data = json.loads(data)
    pdf_bytes = generate_pdf_report(report_data)
    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={
            'Content-Disposition': 'attachment; filename=resume_analysis_report.pdf'
        }
    )


if __name__ == '__main__':
    app.run(debug=True)