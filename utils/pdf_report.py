from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io


def generate_pdf_report(data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)

    navy = HexColor('#1a237e')
    blue = HexColor('#3949ab')
    light_blue = HexColor('#e8eaf6')
    red = HexColor('#c62828')
    green = HexColor('#2e7d32')
    gray = HexColor('#666666')
    light_gray = HexColor('#f5f5f5')

    title_style = ParagraphStyle('Title', fontSize=22, textColor=navy,
                                  alignment=TA_CENTER, spaceAfter=6, fontName='Helvetica-Bold')
    subtitle_style = ParagraphStyle('Subtitle', fontSize=11, textColor=gray,
                                     alignment=TA_CENTER, spaceAfter=20)
    section_style = ParagraphStyle('Section', fontSize=13, textColor=navy,
                                    spaceAfter=8, spaceBefore=16, fontName='Helvetica-Bold')
    body_style = ParagraphStyle('Body', fontSize=10, textColor=black,
                                 spaceAfter=4, leading=14)
    tag_style = ParagraphStyle('Tag', fontSize=9, textColor=blue,
                                spaceAfter=2, leading=12)
    footer_style = ParagraphStyle('Footer', fontSize=9, textColor=gray, alignment=TA_CENTER)

    story = []

    # HEADER
    story.append(Paragraph("ResumeAI -- Analysis Report", title_style))
    filename = data.get('filename', 'Resume')
    story.append(Paragraph(f"Resume: {filename}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=navy))
    story.append(Spacer(1, 0.15*inch))

    # MATCH SCORE
    score = data.get('match_score', 0)
    if score >= 75:
        score_color = green
        label = 'Excellent Match'
    elif score >= 50:
        score_color = blue
        label = 'Good Match'
    elif score >= 30:
        score_color = HexColor('#f57c00')
        label = 'Partial Match'
    else:
        score_color = red
        label = 'Low Match'

    score_data = [[
        Paragraph(f"<font size=26><b>{score}%</b></font>",
                  ParagraphStyle('Score', alignment=TA_CENTER, fontSize=26, textColor=score_color)),
        Paragraph(f"<b>{label}</b><br/><font size=9 color='#666666'>Match score based on TF-IDF + Cosine Similarity</font>",
                  ParagraphStyle('ScoreLabel', fontSize=12, textColor=navy, leading=18))
    ]]
    score_table = Table(score_data, colWidths=[1.5*inch, 5.5*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), light_blue),
        ('BACKGROUND', (1, 0), (1, 0), light_gray),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWPADDING', (0, 0), (-1, -1), 12),
        ('BOX', (0, 0), (-1, -1), 1, HexColor('#e0e0e0')),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.15*inch))

    # RESUME SUMMARY
    story.append(Paragraph("Resume Summary", section_style))
    exp = data.get('experience_years')
    edu = data.get('education', [])
    summary_data = [
        ['Experience', str(exp) + ' years' if exp else 'Not specified'],
        ['Education', ', '.join(edu) if edu else 'Not specified'],
        ['Skills Found', str(len(data.get('skills', []))) + ' skills detected'],
    ]
    summary_table = Table(summary_data, colWidths=[2*inch, 5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), light_blue),
        ('TEXTCOLOR', (0, 0), (0, -1), navy),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e0e0e0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.1*inch))

    # SKILLS
    skills = data.get('skills', [])
    if skills:
        story.append(Paragraph("Skills Found in Resume", section_style))
        story.append(Paragraph(', '.join(skills), tag_style))
        story.append(Spacer(1, 0.1*inch))

    # MATCHED SKILLS
    matched = data.get('matched_skills', [])
    if matched:
        story.append(Paragraph("Matched Skills", section_style))
        story.append(Paragraph(', '.join(matched),
                               ParagraphStyle('Matched', fontSize=10, textColor=green, spaceAfter=4)))
        story.append(Spacer(1, 0.05*inch))

    # MISSING SKILLS
    missing = data.get('missing_skills', [])
    if missing:
        story.append(Paragraph("Missing Skills (from Job Description)", section_style))
        story.append(Paragraph(', '.join(missing),
                               ParagraphStyle('Missing', fontSize=10, textColor=red, spaceAfter=4)))
        story.append(Spacer(1, 0.1*inch))

    # IMPROVEMENT TIPS
    tips = data.get('improvement_tips', [])
    if tips:
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#e0e0e0')))
        story.append(Paragraph("Resume Improvement Tips", section_style))
        for i, tip in enumerate(tips, 1):
            story.append(Paragraph(f"{i}. {tip}", body_style))
        story.append(Spacer(1, 0.1*inch))

    # INTERVIEW QUESTIONS
    questions = data.get('interview_questions', [])
    if questions:
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#e0e0e0')))
        story.append(Paragraph("AI-Generated Interview Questions", section_style))
        for i, q in enumerate(questions, 1):
            story.append(Paragraph(f"{i}. {q}", body_style))
        story.append(Spacer(1, 0.1*inch))

    # FOOTER
    story.append(HRFlowable(width="100%", thickness=2, color=navy))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("Generated by ResumeAI -- AI-Powered Hiring Tool", footer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()