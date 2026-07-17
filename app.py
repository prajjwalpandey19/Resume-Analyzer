import os
import json
from flask import Flask, request, render_template, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from utils.pdf_parser import extract_text_from_pdf, PDFParsingError
from utils.gemini_analyzer import analyze_resume, GeminiAnalysisError
from utils.database_helper import init_db, save_analysis, get_all_analyses, get_analysis, delete_analysis
from utils.pdf_generator import generate_pdf_report

# Load environment variables from absolute path
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "resume_analyzer_secret_key_12984")

# Configure upload directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB limit

# Ensure required directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize SQLite database
init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

@app.route('/')
def home():
    """Renders the Home upload & job description input page."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Handles PDF upload, text parsing, Gemini AI evaluation, and database logging."""
    if 'resume' not in request.files:
        flash("No file part provided.", "error")
        return redirect(url_for('home'))
        
    file = request.files['resume']
    if file.filename == '':
        flash("No file selected. Please upload a PDF resume.", "error")
        return redirect(url_for('home'))
        
    if not allowed_file(file.filename):
        flash("Unsupported file format. Please upload a PDF resume.", "error")
        return redirect(url_for('home'))
        
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        # Save upload file
        file.save(file_path)
        
        # 1. Parse PDF text
        resume_text = extract_text_from_pdf(file_path)
        
        # 2. Extract job description
        job_description = request.form.get('job_description', '').strip()
        
        # 3. Call Gemini AI analyzer
        analysis_result = analyze_resume(resume_text, job_description)
        
        # Insert raw text into analysis JSON for dashboard highlighting
        analysis_result['raw_text'] = resume_text
        
        # Parse fields for SQLite database insert
        ats_score = analysis_result.get('ats_score', 0)
        match_pct = analysis_result.get('job_match', {}).get('match_percentage', 0)
        summary = analysis_result.get('summary', '')
        
        # Collate skills into a flat list for history previews
        extracted_data = analysis_result.get('extracted_data', {})
        skills_list = extracted_data.get('technical_skills', []) + extracted_data.get('soft_skills', [])
        
        # 4. Save results to Database
        record_id = save_analysis(
            filename=filename,
            ats_score=ats_score,
            match_percentage=match_pct,
            resume_summary=summary,
            skills=skills_list,
            analysis_dict=analysis_result
        )
        
        flash("Resume analyzed successfully!", "success")
        return redirect(url_for('view_dashboard', analysis_id=record_id))
        
    except PDFParsingError as pe:
        flash(f"Parsing Error: {str(pe)}", "error")
        return redirect(url_for('home'))
    except GeminiAnalysisError as ge:
        flash(f"AI Analysis Error: {str(ge)}", "error")
        return redirect(url_for('home'))
    except Exception as e:
        flash(f"Unexpected System Error: {str(e)}", "error")
        return redirect(url_for('home'))
    finally:
        # Remove uploaded file immediately to maintain data privacy and save space
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

@app.route('/dashboard/<int:analysis_id>')
def view_dashboard(analysis_id):
    """Displays detailed reports and visualizations for a specific analysis."""
    record = get_analysis(analysis_id)
    if not record:
        flash("Analysis record not found.", "error")
        return redirect(url_for('home'))
        
    analysis_data = record['analysis_json']
    raw_resume_text = analysis_data.get('raw_text', '')
    
    return render_template(
        'dashboard.html',
        analysis=record,
        data=analysis_data,
        raw_resume_text=raw_resume_text
    )

@app.route('/history')
def history_page():
    """Displays searchable list of past analysis logs."""
    search_query = request.args.get('search', '').strip()
    records = get_all_analyses(search_query=search_query if search_query else None)
    return render_template('history.html', analyses=records)

@app.route('/delete/<int:analysis_id>', methods=['POST'])
def delete_analysis_route(analysis_id):
    """Deletes a historical record permanently."""
    success = delete_analysis(analysis_id)
    if success:
        flash("Record deleted successfully.", "success")
    else:
        flash("Failed to delete record.", "error")
    return redirect(url_for('history_page'))

@app.route('/download/<int:analysis_id>')
def download_report(analysis_id):
    """Generates a professional PDF report on the fly and downloads it."""
    record = get_analysis(analysis_id)
    if not record:
        flash("Record not found.", "error")
        return redirect(url_for('home'))
        
    # Generate temporary PDF filename
    pdf_filename = f"Analysis_Report_{analysis_id}.pdf"
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
    
    try:
        generate_pdf_report(record, pdf_path)
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"ATS_Analysis_Report_{record['filename']}",
            mimetype='application/pdf'
        )
    except Exception as e:
        flash(f"Failed to generate PDF Report: {str(e)}", "error")
        return redirect(url_for('view_dashboard', analysis_id=analysis_id))
    finally:
        # File is sent asynchronously, but Flask's send_file can locks the file
        # We can implement a clean-up mechanism, or delete on next request/timed task.
        # ReportLab creates files fast, we can delete it right after serving if we use
        # a custom after-request handler or let it overwrite next time. To be completely safe:
        pass

if __name__ == '__main__':
    app.run(debug=True)
