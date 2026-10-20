import os
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestClassifier
import joblib

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'rf_model.joblib')

def clean_text(text):
    if not text:
        return ""
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z0-9\s\+\#\.\-]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_skill_overlap(student_skills_str, job_skills_str):
    """
    Extracts matched skills and missing skills
    """
    if not student_skills_str or not job_skills_str:
        return {"matched": [], "missing": []}
        
    s_skills = [s.strip().lower() for s in str(student_skills_str).replace(',', '\n').split('\n') if s.strip()]
    j_skills = [s.strip().lower() for s in str(job_skills_str).replace(',', '\n').split('\n') if s.strip()]
    
    matched = []
    missing = []
    
    for req in j_skills:
        found = False
        for s in s_skills:
            if req in s or s in req:
                matched.append(req.title())
                found = True
                break
        if not found:
            missing.append(req.title())
            
    return {
        "matched": list(dict.fromkeys(matched)),
        "missing": list(dict.fromkeys(missing))
    }

def calculate_tfidf_similarity(resume_text, job_text, student_skills="", job_skills=""):
    """
    Computes TF-IDF vectorization and cosine similarity between resume and job description.
    Returns float percentage between 10.0 and 98.5%
    """
    clean_resume = clean_text(resume_text)
    clean_job = clean_text(job_text)
    
    if not clean_resume or not clean_job:
        return 0.0
    
    vectorizer = TfidfVectorizer(
        stop_words='english',
        ngram_range=(1, 2),
        token_pattern=r'(?u)\b[\w\+\#\.\-]+\b'
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform([clean_resume, clean_job])
        raw_sim = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
        
        # Skill overlap ratio
        skills_info = extract_skill_overlap(student_skills, job_skills)
        total_req = len(skills_info['matched']) + len(skills_info['missing'])
        skill_ratio = (len(skills_info['matched']) / total_req) if total_req > 0 else raw_sim
        
        combined = (raw_sim * 55.0) + (skill_ratio * 45.0)
        final_score = float(np.clip(combined, 12.0, 98.5))
        return round(final_score, 1)
    except Exception as e:
        print(f"Error in TF-IDF calculation: {e}")
        return 50.0

class ShortlistPredictor:
    def __init__(self):
        self.model = None
        self._load_or_train_default_model()

    def _load_or_train_default_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                return
            except Exception:
                pass
        
        # Train baseline Random Forest classifier
        np.random.seed(42)
        n_samples = 2000
        
        tfidf = np.random.uniform(20, 95, n_samples)
        cgpa = np.random.uniform(6.0, 9.9, n_samples)
        projects = np.random.randint(0, 8, n_samples)
        certs = np.random.randint(0, 6, n_samples)
        exp = np.random.randint(0, 4, n_samples)
        skill_ratio = np.random.uniform(0.1, 1.0, n_samples)
        
        X = np.column_stack([tfidf, cgpa, projects, certs, exp, skill_ratio])
        
        composite_score = (
            (tfidf / 100.0) * 0.40 +
            ((cgpa - 5.0) / 5.0) * 0.25 +
            (np.minimum(projects, 4) / 4.0) * 0.15 +
            (np.minimum(certs, 3) / 3.0) * 0.10 +
            (np.minimum(exp, 2) / 2.0) * 0.10
        )
        
        noise = np.random.normal(0, 0.03, n_samples)
        y = (composite_score + noise > 0.48).astype(int)
        
        rf = RandomForestClassifier(
            n_estimators=120,
            max_depth=6,
            min_samples_split=4,
            random_state=42
        )
        rf.fit(X, y)
        self.model = rf
        try:
            joblib.dump(self.model, MODEL_PATH)
        except Exception:
            pass

    def predict_shortlist_probability(self, student_profile, internship):
        """
        Calculates probability (0.0 to 100.0) of a candidate being shortlisted.
        Supports both dict (MongoDB) and SQLAlchemy Object models.
        """
        if isinstance(student_profile, dict):
            # Dict extraction
            tech_skills = student_profile.get('technical_skills', '')
            cgpa = float(student_profile.get('cgpa') or 0.0)
            num_projects = len(student_profile.get('projects', []))
            num_certs = len(student_profile.get('certifications', []))
            num_exp = len(student_profile.get('experiences', []))
            
            # Text synthesis
            parts = [
                student_profile.get('full_name', ''),
                student_profile.get('department', ''),
                student_profile.get('college_name', ''),
                student_profile.get('bio', ''),
                tech_skills,
                student_profile.get('soft_skills', ''),
                student_profile.get('career_interests', ''),
            ]
            for p in student_profile.get('projects', []):
                parts.append(f"{p.get('title', '')} {p.get('technologies', '')} {p.get('description', '')}")
            for e in student_profile.get('experiences', []):
                parts.append(f"{e.get('title', '')} {e.get('company_name', '')} {e.get('description', '')}")
            for c in student_profile.get('certifications', []):
                parts.append(f"{c.get('title', '')} {c.get('issuing_organization', '')}")
            for ed in student_profile.get('educations', []):
                parts.append(f"{ed.get('degree', '')} {ed.get('field_of_study', '')} {ed.get('institution', '')}")
            resume_text = " ".join(parts).strip()
        else:
            tech_skills = student_profile.technical_skills or ''
            cgpa = float(student_profile.cgpa or 0.0)
            num_projects = len(student_profile.projects) if hasattr(student_profile, 'projects') else 0
            num_certs = len(student_profile.certifications) if hasattr(student_profile, 'certifications') else 0
            num_exp = len(student_profile.experiences) if hasattr(student_profile, 'experiences') else 0
            resume_text = student_profile.get_full_resume_text()

        if isinstance(internship, dict):
            job_skills = internship.get('required_skills', '')
            job_parts = [
                internship.get('title', ''),
                internship.get('domain', ''),
                job_skills,
                internship.get('description', ''),
                internship.get('responsibilities', ''),
                internship.get('eligibility', ''),
            ]
            job_text = " ".join(job_parts).strip()
        else:
            job_skills = internship.required_skills or ''
            job_text = internship.get_full_job_text()
        
        skill_res = extract_skill_overlap(tech_skills, job_skills)
        total_req = len(skill_res['matched']) + len(skill_res['missing'])
        skill_ratio = (len(skill_res['matched']) / total_req) if total_req > 0 else 0.5
        
        tfidf_score = calculate_tfidf_similarity(
            resume_text,
            job_text,
            tech_skills,
            job_skills
        )
        
        features = np.array([[
            tfidf_score,
            cgpa,
            num_projects,
            num_certs,
            num_exp,
            skill_ratio
        ]])
        
        try:
            proba = self.model.predict_proba(features)[0][1]
            probability_pct = round(float(proba * 100.0), 1)
        except Exception:
            probability_pct = round(float(tfidf_score * 0.6 + (cgpa / 10.0 * 100) * 0.4), 1)
            
        return {
            "tfidf_score": tfidf_score,
            "rf_probability": probability_pct,
            "skill_overlap": skill_res,
            "cgpa": cgpa
        }

shortlist_predictor = ShortlistPredictor()
