import os
import sqlite3
import json
from datetime import datetime

# Set up database path relative to the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'database')
DB_PATH = os.path.join(DB_DIR, 'database.db')

def init_db():
    """Initializes the SQLite database and creates the required table if it doesn't exist."""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            upload_time TEXT NOT NULL,
            filename TEXT NOT NULL,
            ats_score INTEGER,
            match_percentage INTEGER,
            resume_summary TEXT,
            skills TEXT,
            analysis_json TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Returns a sqlite3 connection object that returns rows as dicts."""
    init_db()  # Ensure table exists
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def save_analysis(filename, ats_score, match_percentage, resume_summary, skills, analysis_dict):
    """
    Saves an analysis record to the database.
    
    Args:
        filename (str): Name of the uploaded resume.
        ats_score (int): Calculated ATS score.
        match_percentage (int): Job description match percentage.
        resume_summary (str): AI professional summary.
        skills (list or str): List of skills.
        analysis_dict (dict): The complete Gemini analysis JSON structure.
        
    Returns:
        int: The ID of the inserted record.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Format skills to a comma-separated string if it's a list
    if isinstance(skills, list):
        skills_str = ", ".join(skills)
    else:
        skills_str = str(skills)
        
    upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    analysis_json_str = json.dumps(analysis_dict)
    
    cursor.execute('''
        INSERT INTO analyses (upload_time, filename, ats_score, match_percentage, resume_summary, skills, analysis_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (upload_time, filename, ats_score, match_percentage, resume_summary, skills_str, analysis_json_str))
    
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id

def get_all_analyses(search_query=None):
    """
    Retrieves all analysis records, optionally filtered by filename or skills.
    
    Args:
        search_query (str, optional): Query to search for.
        
    Returns:
        list: List of sqlite3.Row dict-like objects representing matching database rows.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if search_query:
        # Search by filename or skills
        query = "%" + search_query + "%"
        cursor.execute('''
            SELECT id, upload_time, filename, ats_score, match_percentage, resume_summary, skills
            FROM analyses
            WHERE filename LIKE ? OR skills LIKE ?
            ORDER BY id DESC
        ''', (query, query))
    else:
        cursor.execute('''
            SELECT id, upload_time, filename, ats_score, match_percentage, resume_summary, skills
            FROM analyses
            ORDER BY id DESC
        ''')
        
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_analysis(analysis_id):
    """
    Retrieves a single analysis record by ID.
    
    Args:
        analysis_id (int): Database record ID.
        
    Returns:
        dict: The full analysis details including parsed analysis_json, or None if not found.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM analyses WHERE id = ?', (analysis_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        result = dict(row)
        result['analysis_json'] = json.loads(result['analysis_json'])
        return result
    return None

def delete_analysis(analysis_id):
    """
    Deletes an analysis record by ID.
    
    Args:
        analysis_id (int): Database record ID.
        
    Returns:
        bool: True if deleted successfully, False otherwise.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM analyses WHERE id = ?', (analysis_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted
