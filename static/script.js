// ══════════════════════════════════════
// SAFE HELPER
// ══════════════════════════════════════
function safeSet(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

function safeStyle(id, prop, value) {
    const el = document.getElementById(id);
    if (el) el.style[prop] = value;
}

// ══════════════════════════════════════
// MODE TOGGLE
// ══════════════════════════════════════
function switchMode(mode) {
    document.getElementById('btnWithResume').classList.toggle('active', mode === 'resume');
    document.getElementById('btnJDOnly').classList.toggle('active', mode === 'jd');
    document.getElementById('resumeMode').classList.toggle('hidden', mode === 'jd');
    document.getElementById('jdMode').classList.toggle('hidden', mode === 'resume');
}

// ══════════════════════════════════════
// PAGE NAVIGATION
// ══════════════════════════════════════
function showPage(pageName) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.getElementById('page-' + pageName).classList.add('active');
    document.querySelectorAll('.nav-item').forEach(item => {
        if (item.getAttribute('onclick') && item.getAttribute('onclick').includes(pageName)) {
            item.classList.add('active');
        }
    });
}

// ══════════════════════════════════════
// SESSION HISTORY
// ══════════════════════════════════════
let analysisHistory = [];
let interviewCount = 0;

function updateDashboardStats() {
    safeSet('stat-analyzed', analysisHistory.length);
    safeSet('stat-interviews', interviewCount);
    if (analysisHistory.length > 0) {
        const scores = analysisHistory.map(h => h.score);
        const avg = (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1);
        const top = Math.max(...scores).toFixed(1);
        safeSet('stat-avg-score', avg + '%');
        safeSet('stat-top-score', top + '%');
    }
}

function addToHistory(filename, score, matchedSkills, missingSkills) {
    analysisHistory.push({ filename, score, matchedSkills, missingSkills, time: new Date().toLocaleTimeString() });
    updateDashboardStats();
    renderHistory();
}

function renderHistory() {
    const list = document.getElementById('historyList');
    const empty = document.getElementById('historyEmpty');
    if (!list) return;
    if (analysisHistory.length === 0) {
        if (empty) empty.classList.remove('hidden');
        list.innerHTML = '';
        return;
    }
    if (empty) empty.classList.add('hidden');
    list.innerHTML = analysisHistory.slice().reverse().map((h) => `
        <div class="card" style="margin-bottom:1rem;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <strong>${h.filename}</strong>
                    <span style="margin-left:1rem; color:#888; font-size:0.85rem;">${h.time}</span>
                </div>
                <div style="font-size:1.4rem; font-weight:700; color:#1a237e;">${h.score}%</div>
            </div>
            <div style="margin-top:0.8rem;">
                <span style="font-size:0.82rem; color:#555;">Matched: ${h.matchedSkills.slice(0,4).join(', ')}${h.matchedSkills.length > 4 ? '...' : ''}</span><br>
                <span style="font-size:0.82rem; color:#c62828;">Missing: ${h.missingSkills.slice(0,4).join(', ')}${h.missingSkills.length > 4 ? '...' : ''}</span>
            </div>
        </div>
    `).join('');
}

// ══════════════════════════════════════
// SINGLE RESUME ANALYSIS
// ══════════════════════════════════════
document.getElementById('analyzeForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    const resumeFile = document.getElementById('resumeFile').files[0];
    const jobDescription = document.getElementById('jobDescription').value;
    if (!resumeFile || !jobDescription.trim()) {
        alert('Please upload a resume and enter a job description.');
        return;
    }
    document.getElementById('loadingSingle').classList.remove('hidden');
    document.getElementById('resultsSingle').classList.add('hidden');

    const formData = new FormData();
    formData.append('resume', resumeFile);
    formData.append('job_description', jobDescription);

    try {
        const response = await fetch('/analyze', { method: 'POST', body: formData });
        const data = await response.json();
        document.getElementById('loadingSingle').classList.add('hidden');
        if (data.error) { alert(data.error); return; }
        displaySingleResults(data, resumeFile.name);
        document.getElementById('resultsSingle').classList.remove('hidden');
    } catch (error) {
        document.getElementById('loadingSingle').classList.add('hidden');
        alert('Something went wrong: ' + error.message);
    }
});

function displaySingleResults(data, filename) {
    window._lastAnalysisData = data;
    const score = data.match_score || 0;
    safeSet('scoreValue', score + '%');
    safeStyle('scoreCircle', 'background', `conic-gradient(#3949ab ${score}%, #e2e8f0 ${score}%)`);

    const label = score >= 75 ? 'Excellent Match' : score >= 50 ? 'Good Match' : score >= 30 ? 'Partial Match' : 'Low Match';
    safeSet('scoreLabel', label);

    safeSet('expYears', data.experience_years ? data.experience_years + ' years' : 'Not specified');
    safeSet('education', data.education && data.education.length ? data.education.join(', ') : 'Not specified');

    renderTags('skillsList', data.skills);
    renderTags('matchedSkills', data.matched_skills);
    renderTags('missingSkills', data.missing_skills);

    // Tips
    const tipsList = document.getElementById('improvementTips');
    if (tipsList) {
        tipsList.innerHTML = '';
        if (data.tips_error) {
            tipsList.innerHTML = `<div class="error-box">${data.tips_error}</div>`;
        } else {
            (data.improvement_tips || []).forEach(tip => {
                const li = document.createElement('li');
                li.textContent = tip;
                tipsList.appendChild(li);
            });
        }
    }

    // Questions
    const questionsList = document.getElementById('interviewQuestions');
    if (questionsList) {
        questionsList.innerHTML = '';
        if (data.interview_error) {
            questionsList.innerHTML = `<div class="error-box">${data.interview_error}</div>`;
        } else {
            (data.interview_questions || []).forEach(q => {
                const li = document.createElement('li');
                li.textContent = q;
                questionsList.appendChild(li);
            });
        }
    }

    // Skill Confidence Bars
    const confidenceContainer = document.getElementById('skillConfidence');
    if (confidenceContainer) {
        confidenceContainer.innerHTML = '';
        (data.skill_confidence || []).forEach(item => {
            const levelClass = item.level.toLowerCase();
            const bar = document.createElement('div');
            bar.className = 'skill-bar-item';
            bar.innerHTML = `
                <div class="skill-bar-header">
                    <span class="skill-bar-name">${item.skill}</span>
                    <span class="skill-bar-meta">${item.level} • ${item.count}x mentioned</span>
                </div>
                <div class="skill-bar-track">
                    <div class="skill-bar-fill ${levelClass}" style="width: ${item.confidence}%"></div>
                </div>
            `;
            confidenceContainer.appendChild(bar);
        });
    }

    // Bias-Free Screening
    const biasColorMap = { 'Low': '#2e7d32', 'Medium': '#f57c00', 'High': '#c62828', 'Very High': '#b71c1c' };
    const biasScore = data.bias_score || 0;
    const biasColor = biasColorMap[data.bias_risk] || '#2e7d32';
    safeSet('biasScore', biasScore + '%');
    safeStyle('biasCircle', 'background', `conic-gradient(${biasColor} ${biasScore}%, #e2e8f0 ${biasScore}%)`);
    safeSet('biasRisk', 'Bias Risk: ' + (data.bias_risk || '—'));
    safeSet('biasCount', (data.bias_elements_count || 0) + ' bias element(s) detected');

    const biasContainer = document.getElementById('biasDetected');
    if (biasContainer) {
        biasContainer.innerHTML = '';
        if (data.is_bias_free) {
            biasContainer.innerHTML = '<div class="bias-free-badge">Great! No significant bias elements detected.</div>';
        } else {
            const detected = data.bias_detected || {};
            const labels = {
                name: { title: 'Full Name', reason: 'Names can reveal gender, ethnicity or religion — leading to unconscious bias in hiring.' },
                gender_indicators: { title: 'Gender Indicators', reason: 'Gender information can cause discrimination — skills should matter, not gender.' },
                age_dob: { title: 'Age / Date of Birth', reason: 'Age can lead to discrimination — younger or older candidates may be unfairly rejected.' },
                photo: { title: 'Photo Mention', reason: 'Photos introduce appearance-based bias — candidates should be judged on merit only.' },
                marital_status: { title: 'Marital Status', reason: 'Marital status can bias hiring — employers may assume family responsibilities affect work.' },
                religion: { title: 'Religion', reason: 'Religion should never affect hiring — it can cause serious discrimination.' },
                nationality_caste: { title: 'Nationality / Caste', reason: 'Caste and nationality are irrelevant to job performance and can cause unfair bias.' }
            };
            Object.entries(detected).forEach(([key, values]) => {
                const info = labels[key] || { title: key, reason: 'This information may cause unconscious bias.' };
                const div = document.createElement('div');
                div.className = 'bias-item';
                div.innerHTML = `
                    <strong>${info.title}:</strong> ${Array.isArray(values) ? values.join(', ') : values}
                    <br><span style="font-size:0.8rem; color:#795548; margin-top:0.3rem; display:block;">
                    Why bias? ${info.reason}</span>
                `;
                biasContainer.appendChild(div);
            });
        }
    }

    // Fake Resume Detection
    const fakeScore = data.authenticity_score || 0;
    const fakeColorMap = { 'green': '#2e7d32', 'orange': '#f57c00', 'red': '#c62828', 'darkred': '#b71c1c' };
    const fakeColor = fakeColorMap[data.verdict_color] || '#2e7d32';
    safeSet('fakeScore', fakeScore + '%');
    safeStyle('fakeCircle', 'background', `conic-gradient(${fakeColor} ${fakeScore}%, #e2e8f0 ${fakeScore}%)`);
    safeSet('fakeVerdict', 'Verdict: ' + (data.verdict || '—'));
    safeSet('fakeTotalIssues', (data.total_issues || 0) + ' issue(s) found');

    const redFlagsContainer = document.getElementById('fakeRedFlags');
    if (redFlagsContainer) {
        redFlagsContainer.innerHTML = '';
        if (!data.red_flags || data.red_flags.length === 0) {
            redFlagsContainer.innerHTML = '<div class="authentic-badge">No red flags detected!</div>';
        } else {
            (data.red_flags || []).forEach(flag => {
                const div = document.createElement('div');
                div.className = 'red-flag-item';
                div.innerHTML = `<strong>🚩 ${flag.type} (${flag.severity}):</strong> ${flag.detail}`;
                redFlagsContainer.appendChild(div);
            });
        }
    }

    const warningsContainer = document.getElementById('fakeWarnings');
    if (warningsContainer) {
        warningsContainer.innerHTML = '';
        (data.warnings || []).forEach(warning => {
            const div = document.createElement('div');
            div.className = 'warning-item';
            div.innerHTML = `<strong>⚠️ ${warning.type}:</strong> ${warning.detail}`;
            warningsContainer.appendChild(div);
        });
    }

    // ATS Results
    const atsColorMap = { green: '#2e7d32', blue: '#3949ab', orange: '#f57c00', red: '#c62828' };
    const atsScore = data.ats_score || 0;
    const atsColorHex = atsColorMap[data.ats_color] || '#3949ab';
    safeSet('atsScoreValue', atsScore + '%');
    safeStyle('atsScoreCircle', 'background', `conic-gradient(${atsColorHex} ${atsScore}%, #e2e8f0 ${atsScore}%)`);
    safeSet('atsRating', 'ATS Rating: ' + (data.ats_rating || '—'));
    safeSet('atsWordCount', 'Word Count: ' + (data.ats_word_count || 0) + ' words');

    const atsPassed = document.getElementById('atsPassed');
    if (atsPassed) {
        atsPassed.innerHTML = '';
        (data.ats_passed || []).forEach(p => {
            const li = document.createElement('li');
            li.textContent = p;
            atsPassed.appendChild(li);
        });
    }

    const atsIssues = document.getElementById('atsIssues');
    if (atsIssues) {
        atsIssues.innerHTML = '';
        (data.ats_issues || []).forEach(issue => {
            const li = document.createElement('li');
            li.textContent = issue;
            atsIssues.appendChild(li);
        });
    }

    addToHistory(filename, score, data.matched_skills || [], data.missing_skills || []);
}

function renderTags(containerId, items) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';
    if (!items || items.length === 0) {
        container.innerHTML = '<span style="opacity:0.5; font-size:0.85rem;">None found</span>';
        return;
    }
    items.forEach(item => {
        const span = document.createElement('span');
        span.textContent = item;
        container.appendChild(span);
    });
}

// ══════════════════════════════════════
// JD ONLY MODE
// ══════════════════════════════════════
document.addEventListener('DOMContentLoaded', function() {
    const jdForm = document.getElementById('jdOnlyForm');
    if (jdForm) {
        jdForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const jdText = document.getElementById('jdOnlyText').value;
            if (!jdText.trim()) { alert('Please paste a job description.'); return; }

            document.getElementById('loadingJD').classList.remove('hidden');
            document.getElementById('resultsJD').classList.add('hidden');

            const formData = new FormData();
            formData.append('job_description', jdText);

            try {
                const response = await fetch('/analyze-jd', { method: 'POST', body: formData });
                const data = await response.json();
                document.getElementById('loadingJD').classList.add('hidden');
                if (data.error) { alert(data.error); return; }
                displayJDResults(data);
                document.getElementById('resultsJD').classList.remove('hidden');
            } catch (error) {
                document.getElementById('loadingJD').classList.add('hidden');
                alert('Something went wrong: ' + error.message);
            }
        });
    }
});

function displayJDResults(data) {
    safeSet('jdLevel', data.experience_level || '—');
    safeSet('jdCompetition', data.competition || '—');
    safeSet('jdTotalSkills', data.total_skills || '0');
    safeSet('jdEducation', data.education_required && data.education_required.length ? data.education_required.join(', ') : 'Not specified');

    renderTags('jdSkills', data.required_skills);

    const profileList = document.getElementById('jdIdealProfile');
    if (profileList) {
        profileList.innerHTML = '';
        (data.ideal_profile || []).forEach(tip => {
            const li = document.createElement('li');
            li.textContent = tip;
            profileList.appendChild(li);
        });
    }

    const questionsList = document.getElementById('jdInterviewQuestions');
    if (questionsList) {
        questionsList.innerHTML = '';
        (data.interview_questions || []).forEach(q => {
            const li = document.createElement('li');
            li.textContent = q;
            questionsList.appendChild(li);
        });
    }
}

// ══════════════════════════════════════
// RANK MULTIPLE RESUMES
// ══════════════════════════════════════
document.getElementById('rankForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    const resumeFiles = document.getElementById('resumeFiles').files;
    const jobDescription = document.getElementById('jobDescriptionMulti').value;
    if (resumeFiles.length === 0 || !jobDescription.trim()) {
        alert('Please upload resumes and enter a job description.');
        return;
    }
    document.getElementById('loadingMulti').classList.remove('hidden');
    document.getElementById('resultsMulti').classList.add('hidden');

    const formData = new FormData();
    for (let i = 0; i < resumeFiles.length; i++) {
        formData.append('resumes', resumeFiles[i]);
    }
    formData.append('job_description', jobDescription);

    try {
        const response = await fetch('/rank', { method: 'POST', body: formData });
        const data = await response.json();
        document.getElementById('loadingMulti').classList.add('hidden');
        if (data.error) { alert(data.error); return; }
        displayRankResults(data.ranked_resumes);
        document.getElementById('resultsMulti').classList.remove('hidden');
    } catch (error) {
        document.getElementById('loadingMulti').classList.add('hidden');
        alert('Something went wrong: ' + error.message);
    }
});

function displayRankResults(rankedResumes) {
    const tbody = document.getElementById('rankTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';
    rankedResumes.forEach((resume, index) => {
        const rating = resume.score >= 75 ? 'Excellent' : resume.score >= 50 ? 'Good' : resume.score >= 30 ? 'Fair' : 'Low';
        const row = document.createElement('tr');
        row.innerHTML = `<td>#${index + 1}</td><td>${resume.name}</td><td><strong>${resume.score}%</strong></td><td>${rating}</td>`;
        tbody.appendChild(row);
    });
}

// ══════════════════════════════════════
// VOICE MOCK INTERVIEW
// ══════════════════════════════════════
let voiceQuestions = [];
let currentQuestion = 0;
let recognition = null;
let isRecording = false;
let synth = window.speechSynthesis;

function startVoiceInterview() {
    const jd = document.getElementById('voiceJD').value;
    const skillsInput = document.getElementById('voiceSkills').value;
    const skills = skillsInput.split(',').map(s => s.trim()).filter(Boolean);

    voiceQuestions = generateVoiceQuestions(skills, jd);
    currentQuestion = 0;
    interviewCount++;
    updateDashboardStats();

    document.getElementById('voiceSection').classList.remove('hidden');
    safeSet('qTotal', voiceQuestions.length);

    const list = document.getElementById('voiceQuestionsList');
    if (list) {
        list.innerHTML = '';
        voiceQuestions.forEach((q) => {
            const li = document.createElement('li');
            li.textContent = q;
            list.appendChild(li);
        });
    }
    loadQuestion();
}

function generateVoiceQuestions(skills, jd) {
    const skillQuestions = {
        'python': ['Explain the difference between a list and a tuple in Python.'],
        'machine learning': ['Walk me through how you would approach a machine learning problem from scratch.'],
        'flask': ['How would you structure a Flask application for production?'],
        'sql': ['How do you optimize a slow SQL query?'],
        'data analysis': ['Describe a data analysis project you have worked on end-to-end.'],
        'nlp': ['What is the difference between stemming and lemmatization?'],
        'deep learning': ['Explain how backpropagation works in a neural network.'],
        'git': ['Walk me through your Git workflow when working on a team project.'],
    };

    let questions = [];
    skills.forEach(skill => {
        const key = skill.toLowerCase();
        if (skillQuestions[key]) questions.push(skillQuestions[key][0]);
    });

    const general = [
        'Tell me about yourself and your technical background.',
        'Describe a challenging project you worked on.',
        'How do you stay updated with the latest technology trends?',
        'Where do you see yourself in 3 years?',
        'Tell me about a time you had to learn something new quickly.',
        'How do you handle tight deadlines and pressure?',
        'Why are you interested in this role?',
        'What is your greatest technical strength?',
    ];

    while (questions.length < 8) {
        const q = general[questions.length % general.length];
        if (!questions.includes(q)) questions.push(q);
        else break;
    }
    return questions.slice(0, 8);
}

function loadQuestion() {
    safeSet('qNum', currentQuestion + 1);
    safeSet('voiceQuestion', voiceQuestions[currentQuestion]);
    const transcript = document.getElementById('transcript');
    if (transcript) transcript.classList.add('hidden');
    safeSet('transcriptText', '');
    const btn = document.getElementById('recordBtn');
    if (btn) { btn.textContent = 'Record Answer'; btn.classList.remove('recording'); }
    isRecording = false;
    if (recognition) { recognition.stop(); recognition = null; }
}

function readQuestion() {
    if (synth.speaking) synth.cancel();
    const utterance = new SpeechSynthesisUtterance(voiceQuestions[currentQuestion]);
    utterance.rate = 0.9;
    synth.speak(utterance);
}

function toggleRecording() {
    if (isRecording) stopRecording(); else startRecording();
}

function startRecording() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) { alert('Please use Chrome for speech recognition.'); return; }
    recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.onresult = function(event) {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        safeSet('transcriptText', transcript);
        const t = document.getElementById('transcript');
        if (t) t.classList.remove('hidden');
    };
    recognition.start();
    isRecording = true;
    const btn = document.getElementById('recordBtn');
    if (btn) { btn.textContent = 'Stop Recording'; btn.classList.add('recording'); }
}

function stopRecording() {
    if (recognition) { recognition.stop(); recognition = null; }
    isRecording = false;
    const btn = document.getElementById('recordBtn');
    if (btn) { btn.textContent = 'Record Answer'; btn.classList.remove('recording'); }
}

function nextQuestion() {
    stopRecording();
    if (synth.speaking) synth.cancel();
    if (currentQuestion < voiceQuestions.length - 1) {
        currentQuestion++;
        loadQuestion();
    } else {
        safeSet('voiceQuestion', 'Interview Complete! Great job!');
        safeStyle('voiceQuestion', 'color', '#2e7d32');
    }
}

// ══════════════════════════════════════
// PDF REPORT DOWNLOAD
// ══════════════════════════════════════
function downloadReport() {
    if (!window._lastAnalysisData) { alert('Please analyze a resume first!'); return; }
    const data = window._lastAnalysisData;
    const latest = analysisHistory[analysisHistory.length - 1];
    const formData = new FormData();
    formData.append('report_data', JSON.stringify({
        filename: latest ? latest.filename : 'Resume',
        match_score: data.match_score,
        skills: data.skills,
        education: data.education,
        experience_years: data.experience_years,
        matched_skills: data.matched_skills,
        missing_skills: data.missing_skills,
        improvement_tips: data.improvement_tips,
        interview_questions: data.interview_questions
    }));
    fetch('/download-report', { method: 'POST', body: formData })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'resume_analysis_report.pdf';
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(err => alert('Error: ' + err.message));
}