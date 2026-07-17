# AI Resume Analyzer

An advanced, AI-powered **ATS Resume Evaluation & Matching** web application. It parses PDF resumes, analyzes formatting, extracts skills and certificates, provides an overall ATS score, and matches the content against a specific Job Description using Google Gemini API. The system stores history in an SQLite database and generates downloadable PDF reports.

## Features

- **ATS Compatibility Score (0-100)**: Evaluates structural design, formatting, keyword densities, and quality.
- **Job Match Percentage**: Compares resume text to a pasted Job Description, giving a percentage rating, and listing matching, missing, and recommended keywords.
- **AI-Powered Recommendations**: Extract strengths, weaknesses, and clear actionable improvement suggestions.
- **Skill Extraction & Visualization**: Automatically lists technical vs. soft skills and graphs the proportions using Chart.js.
- **Interactive Highlight**: Dynamically highlights matching keywords directly on the rendered resume text.
- **Analysis History**: Logs all evaluations with dates, filenames, and scores. Includes search filter and row deletion.
- **Export PDF Report**: Compiles a professional ReportLab PDF summary of the ATS score, job match, resume summary, and HR feedback.
- **Theme Switcher**: Fully-featured Light and Dark mode using variables.

---

## Directory Structure

```text
Resume Analyzer/
├── app.py                      # Main entrypoint and routes
├── requirements.txt            # Python dependencies
├── README.md                   # Setup guide
├── database/
│   └── database.db             # SQLite database (auto-created)
├── static/
│   ├── css/
│   │   └── style.css           # CSS stylesheet (Dark/Light mode layout)
│   └── js/
│       └── main.js             # Client-side drag-drop, charts, highlighting
├── templates/
│   ├── base.html               # Shared navigation & page shell
│   ├── index.html              # Landing file drop zone
│   ├── dashboard.html          # Dynamic analysis view
│   └── history.html            # Searchable records database
└── utils/
    ├── database_helper.py      # SQLite CRUD operations
    ├── gemini_analyzer.py      # Gemini JSON structured prompt handler
    ├── pdf_generator.py        # ReportLab PDF building script
    └── pdf_parser.py           # pdfplumber text extraction
```

---

## Installation & Setup

### 1. Prerequisites
Make sure you have **Python 3.9+** and **Git** installed on your system.

### 2. Clone the Repository
If you haven't cloned it yet:
```bash
git clone https://github.com/prajjwalpandey19/Resume-Analyzer.git
cd Resume-Analyzer
```

### 3. Setup Virtual Environment
Create and activate a virtual environment:

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Create a `.env` file in the root of the project:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
FLASK_SECRET_KEY=change_this_to_a_secure_random_string
```

### 6. Run the Application
Start the Flask development server:
```bash
python app.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.

---

## Technical Details

- **Backend**: Python Flask handles file processing, routes, database transactions, and PDF compilation.
- **AI Model**: Google Gemini API via `google-generativeai` utilizing JSON schema extraction mode.
- **Database**: SQLite3 storage for fast local persistence.
- **Frontend**: Bootstrap 5 framework, custom CSS variable toggle, Font Awesome 6 icons, Chart.js for data visualization, and Vanilla JS for interactive features.
