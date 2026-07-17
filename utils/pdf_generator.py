import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_pdf_report(analysis_data, output_path):
    """
    Generates a professional PDF report of the resume analysis using ReportLab.
    
    Args:
        analysis_data (dict): The full analysis dictionary from the DB.
        output_path (str): File path to save the generated PDF.
    """
    # Create the document template
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    primary_color = colors.HexColor("#0f172a")    # Slate 900
    secondary_color = colors.HexColor("#2563eb")  # Blue 600
    text_color = colors.HexColor("#334155")       # Slate 700
    light_bg = colors.HexColor("#f8fafc")         # Slate 50
    border_color = colors.HexColor("#e2e8f0")     # Slate 200
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=25
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=secondary_color,
        spaceBefore=15,
        spaceAfter=8,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=text_color,
        spaceAfter=8
    )
    
    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=text_color,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=5
    )
    
    score_label_style = ParagraphStyle(
        'ScoreLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=primary_color,
        alignment=1 # Center
    )
    
    score_value_style = ParagraphStyle(
        'ScoreValue',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=secondary_color,
        alignment=1 # Center
    )

    story = []
    
    # 1. Header (Title and Subtitle)
    story.append(Paragraph("AI Resume Analyzer Report", title_style))
    filename = analysis_data.get('filename', 'Resume')
    date_str = analysis_data.get('upload_time', '')
    story.append(Paragraph(f"Analyzed Document: {filename}   |   Date: {date_str}", subtitle_style))
    story.append(Spacer(1, 10))
    
    # 2. Score Section (ATS and Job Match)
    ats_score = analysis_data.get('ats_score', 0)
    match_pct = analysis_data.get('match_percentage', 0)
    
    score_data = [
        [
            Paragraph("ATS Compatibility Score", score_label_style),
            Paragraph("Job Description Match", score_label_style)
        ],
        [
            Paragraph(f"{ats_score} / 100", score_value_style),
            Paragraph(f"{match_pct}%" if match_pct > 0 else "N/A", score_value_style)
        ]
    ]
    
    score_table = Table(score_data, colWidths=[250, 250])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,0), 2),
        ('TOPPADDING', (0,0), (-1,1), 10),
        ('BOTTOMPADDING', (0,0), (-1,1), 15),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('INNERGRID', (0,0), (-1,-1), 1, border_color),
    ]))
    
    story.append(score_table)
    story.append(Spacer(1, 20))
    
    # 3. Resume Summary
    story.append(Paragraph("Professional Resume Summary", h1_style))
    summary_text = analysis_data.get('resume_summary', 'No summary available.')
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 15))
    
    # 4. Skills Section
    # Extract sub-components from the full JSON payload
    full_json = analysis_data.get('analysis_json', {})
    extracted_data = full_json.get('extracted_data', {})
    
    tech_skills = extracted_data.get('technical_skills', [])
    soft_skills = extracted_data.get('soft_skills', [])
    
    story.append(Paragraph("Skills Profile", h1_style))
    if tech_skills:
        story.append(Paragraph(f"<b>Technical Skills:</b> {', '.join(tech_skills)}", body_style))
    if soft_skills:
        story.append(Paragraph(f"<b>Soft Skills:</b> {', '.join(soft_skills)}", body_style))
    if not tech_skills and not soft_skills:
        story.append(Paragraph("No skills extracted.", body_style))
    story.append(Spacer(1, 15))
    
    # 5. Job Match Analysis (if Job Description is provided)
    job_match = full_json.get('job_match', {})
    matching_skills = job_match.get('matching_skills', [])
    missing_skills = job_match.get('missing_skills', [])
    recommended_skills = job_match.get('recommended_skills', [])
    
    if match_pct > 0 or matching_skills or missing_skills or recommended_skills:
        story.append(Paragraph("Job Description Matching Details", h1_style))
        if matching_skills:
            story.append(Paragraph(f"<b>Matching Keywords/Skills:</b> {', '.join(matching_skills)}", body_style))
        if missing_skills:
            story.append(Paragraph(f"<b>Missing Keywords/Skills:</b> {', '.join(missing_skills)}", body_style))
        if recommended_skills:
            story.append(Paragraph(f"<b>Recommended Skills to Add:</b> {', '.join(recommended_skills)}", body_style))
        story.append(Spacer(1, 15))
        
    # 6. Strengths, Weaknesses, and Improvements
    analysis_points = full_json.get('analysis', {})
    strengths = analysis_points.get('strengths', [])
    weaknesses = analysis_points.get('weaknesses', [])
    improvements = analysis_points.get('improvements', [])
    
    if strengths or weaknesses or improvements:
        story.append(Paragraph("Detailed HR Evaluation", h1_style))
        
        eval_items = []
        if strengths:
            eval_items.append(Paragraph("<b>Strengths:</b>", body_style))
            for s in strengths:
                eval_items.append(Paragraph(f"&bull; {s}", bullet_style))
            eval_items.append(Spacer(1, 5))
            
        if weaknesses:
            eval_items.append(Paragraph("<b>Areas of Concern / Weaknesses:</b>", body_style))
            for w in weaknesses:
                eval_items.append(Paragraph(f"&bull; {w}", bullet_style))
            eval_items.append(Spacer(1, 5))
            
        if improvements:
            eval_items.append(Paragraph("<b>Recommended Improvements:</b>", body_style))
            for imp in improvements:
                eval_items.append(Paragraph(f"&bull; {imp}", bullet_style))
                
        story.append(KeepTogether(eval_items))
        story.append(Spacer(1, 15))
        
    # 7. Education & Experience Summary (Brief)
    edu_list = extracted_data.get('education', [])
    exp_list = extracted_data.get('work_experience', [])
    
    if edu_list or exp_list:
        story.append(PageBreak())  # Push history/data to second page to keep it clean
        story.append(Paragraph("Extracted Career Profile", title_style))
        story.append(Spacer(1, 10))
        
        if exp_list:
            story.append(Paragraph("Work Experience", h1_style))
            for exp in exp_list:
                role = exp.get('role', 'N/A')
                company = exp.get('company', 'N/A')
                duration = exp.get('duration', 'N/A')
                desc = exp.get('description', '')
                story.append(Paragraph(f"<b>{role}</b> at <i>{company}</i> ({duration})", body_style))
                if desc:
                    story.append(Paragraph(desc, bullet_style))
                story.append(Spacer(1, 5))
                
        if edu_list:
            story.append(Paragraph("Education", h1_style))
            for edu in edu_list:
                degree = edu.get('degree', 'N/A')
                inst = edu.get('institution', 'N/A')
                year = edu.get('year', 'N/A')
                story.append(Paragraph(f"<b>{degree}</b> - {inst} ({year})", body_style))
                story.append(Spacer(1, 5))

    # Build the document
    doc.build(story)
