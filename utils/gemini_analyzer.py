import os
import json
import google.generativeai as genai

class GeminiAnalysisError(Exception):
    """Custom exception for Gemini API and analysis issues."""
    pass

def analyze_resume(resume_text, job_description=None):
    """
    Analyzes the resume text and compares it against the job description (if provided)
    using the Google Gemini API.
    
    Args:
        resume_text (str): The extracted text of the resume.
        job_description (str, optional): The job description to compare against.
        
    Returns:
        dict: Parsed analysis results.
        
    Raises:
        GeminiAnalysisError: If the API call fails or the response cannot be parsed.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise GeminiAnalysisError(
            "Gemini API key is not configured. Please set the GEMINI_API_KEY environment variable."
        )
        
    try:
        genai.configure(api_key=api_key)
        
        # System instructions or clear prompting for structured JSON
        prompt = f"""
You are an expert HR Specialist and ATS (Applicant Tracking System) optimization tool. 
Analyze the following resume text and compare it with the provided Job Description (if available).

Deliver your complete analysis in JSON format matching the schema below. Do not output anything other than a single valid JSON object.

JSON Schema:
{{
  "summary": "A professional 3-4 sentence summary of the candidate's profile, highlighting key experience and background.",
  "ats_score": 85, // Overall ATS score (0-100) based on industry standards, formatting, formatting, skills, experience, and match if JD is provided.
  "ats_breakdown": {{
    "formatting": 80, // Score 0-100 on structure, formatting readability
    "keywords": 80,   // Score 0-100 on standard keyword density
    "skills": 80,     // Score 0-100 on skills section quality
    "education": 80,  // Score 0-100 on education detail clarity
    "experience": 80, // Score 0-100 on experience depth & presentation
    "job_description_match": 80 // Score 0-100 (Set to 0 if Job Description is NOT provided)
  }},
  "job_match": {{
    "match_percentage": 75, // Matching percentage 0-100 (Set to 0 if Job Description is NOT provided)
    "matching_skills": ["skill1", "skill2"], // Skills present in both resume and Job Description (Empty array if Job Description is NOT provided)
    "missing_skills": ["skill3", "skill4"], // Skills mentioned in Job Description but missing from resume (Empty array if Job Description is NOT provided)
    "recommended_skills": ["skill5", "skill6"] // Additional skills related to the JD that the candidate should consider adding (Empty array if Job Description is NOT provided)
  }},
  "extracted_data": {{
    "technical_skills": ["skill1", "skill2"], // List all technical/hard skills found in the resume
    "soft_skills": ["skill1", "skill2"],      // List soft skills (e.g. communication, leadership) found in the resume
    "projects": [
      {{
        "title": "Project Name",
        "description": "Brief description of project achievements/technologies used."
      }}
    ],
    "education": [
      {{
        "degree": "Degree (e.g. B.S. Computer Science)",
        "institution": "University / College",
        "year": "Graduation Year (e.g. 2024 or Ongoing)"
      }}
    ],
    "work_experience": [
      {{
        "role": "Job Title",
        "company": "Company Name",
        "duration": "Duration (e.g. Jun 2022 - Present)",
        "description": "Brief summary of responsibilities and achievements."
      }}
    ],
    "certifications": ["Cert 1", "Cert 2"] // List of professional certifications
  }},
  "analysis": {{
    "strengths": ["Strength 1", "Strength 2"], // Areas where the resume excels
    "weaknesses": ["Weakness 1", "Weakness 2"], // Gaps or areas of concern in the resume
    "improvements": ["Improvement 1", "Improvement 2"] // Actionable advice to improve the resume or increase ATS match
  }}
}}

Resume Text:
---
{resume_text}
---

Job Description:
---
{job_description if job_description else "NO JOB DESCRIPTION PROVIDED"}
---
"""

        # Using gemini-1.5-flash for general text analysis
        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            generation_config={"response_mime_type": "application/json"}
        )
        
        response = model.generate_content(prompt)
        
        if not response or not response.text:
            raise GeminiAnalysisError("Empty response received from Gemini API.")
            
        result = json.loads(response.text)
        return result
        
    except json.JSONDecodeError as je:
        raise GeminiAnalysisError(f"Failed to parse Gemini response as JSON. Raw response: {response.text}")
    except Exception as e:
        raise GeminiAnalysisError(f"Gemini API Error: {str(e)}")
