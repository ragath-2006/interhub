import os
from datetime import datetime
from pymongo import MongoClient
import mongomock
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/internhub_db')

def get_mongo_db():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1500)
        client.server_info()
        print("Connected to Live MongoDB Database successfully at:", MONGO_URI)
        db_name = MONGO_URI.split('/')[-1].split('?')[0] or 'internhub_db'
        return client[db_name]
    except Exception as e:
        print(f"Notice: Live MongoDB not detected ({e}). Using MongoMock in-memory driver.")
        client = mongomock.MongoClient()
        return client['internhub_db']

db = get_mongo_db()

# Collections
users_col = db['users']
students_col = db['students']
companies_col = db['companies']
internships_col = db['internships']
applications_col = db['applications']
reviews_col = db['reviews']
notifications_col = db['notifications']

class MongoHelper:
    @staticmethod
    def to_id(val):
        if isinstance(val, ObjectId):
            return val
        try:
            return ObjectId(str(val))
        except Exception:
            return val

    @staticmethod
    def format_doc(doc):
        if not doc:
            return None
        doc['id'] = str(doc['_id'])
        return doc

    @staticmethod
    def create_user(email, password, role='student'):
        pwd_hash = generate_password_hash(password)
        user_doc = {
            'email': email.strip().lower(),
            'password_hash': pwd_hash,
            'role': role,
            'is_active': True,
            'created_at': datetime.utcnow()
        }
        res = users_col.insert_one(user_doc)
        user_doc['id'] = str(res.inserted_id)
        user_doc['_id'] = res.inserted_id
        return user_doc

    @staticmethod
    def get_user_by_id(user_id):
        u = users_col.find_one({'_id': MongoHelper.to_id(user_id)})
        return MongoHelper.format_doc(u)

    @staticmethod
    def get_user_by_email(email):
        u = users_col.find_one({'email': email.strip().lower()})
        return MongoHelper.format_doc(u)

    @staticmethod
    def check_password(user_doc, password):
        if not user_doc or 'password_hash' not in user_doc:
            return False
        return check_password_hash(user_doc['password_hash'], password)

    @staticmethod
    def get_student_by_user_id(user_id):
        s = students_col.find_one({'user_id': str(user_id)})
        if not s:
            s = students_col.find_one({'user_id': MongoHelper.to_id(user_id)})
        if s:
            s = MongoHelper.format_doc(s)
            s['user'] = MongoHelper.get_user_by_id(s['user_id'])
            # Attach related applications
            s['applications'] = list(applications_col.find({'student_id': str(s['id'])}))
        return s

    @staticmethod
    def get_company_by_user_id(user_id):
        c = companies_col.find_one({'user_id': str(user_id)})
        if not c:
            c = companies_col.find_one({'user_id': MongoHelper.to_id(user_id)})
        if c:
            c = MongoHelper.format_doc(c)
            c['user'] = MongoHelper.get_user_by_id(c['user_id'])
            revs = list(reviews_col.find({'company_id': str(c['id'])}))
            c['total_reviews'] = len(revs)
            c['average_rating'] = round(sum(r.get('rating', 5) for r in revs) / len(revs), 1) if revs else 0.0
            c['internships'] = list(internships_col.find({'company_id': str(c['id'])}))
        return c

    @staticmethod
    def get_company_by_id(company_id):
        c = companies_col.find_one({'_id': MongoHelper.to_id(company_id)})
        if c:
            c = MongoHelper.format_doc(c)
            c['user'] = MongoHelper.get_user_by_id(c['user_id'])
            revs = list(reviews_col.find({'company_id': str(company_id)}))
            c['total_reviews'] = len(revs)
            c['average_rating'] = round(sum(r.get('rating', 5) for r in revs) / len(revs), 1) if revs else 0.0
            c['internships'] = list(internships_col.find({'company_id': str(company_id)}))
        return c

    @staticmethod
    def get_internship_by_id(internship_id):
        job = internships_col.find_one({'_id': MongoHelper.to_id(internship_id)})
        if job:
            job = MongoHelper.format_doc(job)
            comp = MongoHelper.get_company_by_id(job['company_id'])
            job['company'] = comp
            job['applications'] = list(applications_col.find({'internship_id': str(job['id'])}))
        return job

    @staticmethod
    def get_student_resume_text(student_doc):
        if not student_doc:
            return ""
        parts = [
            student_doc.get('full_name', ''),
            student_doc.get('department', ''),
            student_doc.get('college_name', ''),
            student_doc.get('bio', ''),
            student_doc.get('technical_skills', ''),
            student_doc.get('soft_skills', ''),
            student_doc.get('career_interests', ''),
        ]
        for p in student_doc.get('projects', []):
            parts.append(f"{p.get('title', '')} {p.get('technologies', '')} {p.get('description', '')}")
        for e in student_doc.get('experiences', []):
            parts.append(f"{e.get('title', '')} {e.get('company_name', '')} {e.get('description', '')}")
        for c in student_doc.get('certifications', []):
            parts.append(f"{c.get('title', '')} {c.get('issuing_organization', '')}")
        for ed in student_doc.get('educations', []):
            parts.append(f"{ed.get('degree', '')} {ed.get('field_of_study', '')} {ed.get('institution', '')}")
        return " ".join([p for p in parts if p]).strip()

    @staticmethod
    def get_job_text(job_doc):
        if not job_doc:
            return ""
        parts = [
            job_doc.get('title', ''),
            job_doc.get('domain', ''),
            job_doc.get('required_skills', ''),
            job_doc.get('description', ''),
            job_doc.get('responsibilities', ''),
            job_doc.get('eligibility', ''),
        ]
        return " ".join(parts)
