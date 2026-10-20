from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student') # 'student', 'company', 'admin'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    company_profile = db.relationship('CompanyProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    college_name = db.Column(db.String(150))
    department = db.Column(db.String(100))
    year_of_study = db.Column(db.String(30)) # e.g. '3rd Year', 'Final Year'
    cgpa = db.Column(db.Float, default=0.0)
    bio = db.Column(db.Text)
    location = db.Column(db.String(100))
    career_interests = db.Column(db.String(255))
    technical_skills = db.Column(db.Text) # Comma separated list of skills e.g. "Python, Flask, React, SQL, Machine Learning"
    soft_skills = db.Column(db.Text)      # Comma separated e.g. "Communication, Teamwork, Problem Solving"
    github_url = db.Column(db.String(200))
    linkedin_url = db.Column(db.String(200))
    portfolio_url = db.Column(db.String(200))
    avatar = db.Column(db.String(255), default='default-avatar.png')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Dynamic Resume Components
    educations = db.relationship('Education', backref='student', cascade='all, delete-orphan', order_by='Education.end_year.desc()')
    experiences = db.relationship('Experience', backref='student', cascade='all, delete-orphan')
    projects = db.relationship('Project', backref='student', cascade='all, delete-orphan')
    certifications = db.relationship('Certification', backref='student', cascade='all, delete-orphan')
    applications = db.relationship('Application', backref='student', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='student', cascade='all, delete-orphan')

    def get_full_resume_text(self):
        """Builds a comprehensive text snapshot of the student profile for TF-IDF / NLP parsing"""
        parts = [
            self.full_name or '',
            self.department or '',
            self.college_name or '',
            self.bio or '',
            self.technical_skills or '',
            self.soft_skills or '',
            self.career_interests or '',
        ]
        for p in self.projects:
            parts.append(f"{p.title} {p.technologies} {p.description}")
        for e in self.experiences:
            parts.append(f"{e.title} {e.company_name} {e.description}")
        for c in self.certifications:
            parts.append(f"{c.title} {c.issuing_organization}")
        for ed in self.educations:
            parts.append(f"{ed.degree} {ed.field_of_study} {ed.institution}")
        return " ".join([p for p in parts if p]).strip()


class Education(db.Model):
    __tablename__ = 'educations'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    degree = db.Column(db.String(100), nullable=False)
    institution = db.Column(db.String(150), nullable=False)
    field_of_study = db.Column(db.String(100))
    start_year = db.Column(db.String(10))
    end_year = db.Column(db.String(10))
    grade_or_cgpa = db.Column(db.String(20))


class Experience(db.Model):
    __tablename__ = 'experiences'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(100))
    start_date = db.Column(db.String(30))
    end_date = db.Column(db.String(30))
    is_current = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    technologies = db.Column(db.String(200))
    project_url = db.Column(db.String(200))
    description = db.Column(db.Text)


class Certification(db.Model):
    __tablename__ = 'certifications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    issuing_organization = db.Column(db.String(150), nullable=False)
    issue_date = db.Column(db.String(30))
    credential_url = db.Column(db.String(200))


class CompanyProfile(db.Model):
    __tablename__ = 'company_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    company_name = db.Column(db.String(120), nullable=False)
    industry = db.Column(db.String(100))
    website = db.Column(db.String(150))
    location = db.Column(db.String(100))
    description = db.Column(db.Text)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    is_verified = db.Column(db.Boolean, default=True)
    logo = db.Column(db.String(255), default='default-company.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    internships = db.relationship('Internship', backref='company', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='company', cascade='all, delete-orphan')

    @property
    def average_rating(self):
        revs = self.reviews
        if not revs:
            return 0.0
        return round(sum(r.rating for r in revs) / len(revs), 1)

    @property
    def total_reviews(self):
        return len(self.reviews)


class Internship(db.Model):
    __tablename__ = 'internships'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company_profiles.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    domain = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.Text, nullable=False)
    responsibilities = db.Column(db.Text)
    eligibility = db.Column(db.Text)
    min_cgpa = db.Column(db.Float, default=0.0)
    stipend = db.Column(db.String(50), default='Unpaid')
    location = db.Column(db.String(100), default='Remote')
    work_mode = db.Column(db.String(30), default='Remote') # 'Remote', 'On-site', 'Hybrid'
    duration_months = db.Column(db.Integer, default=3)
    vacancies = db.Column(db.Integer, default=1)
    deadline = db.Column(db.String(30))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    applications = db.relationship('Application', backref='internship', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='internship', cascade='all, delete-orphan')

    def get_full_job_text(self):
        """Builds text content of the internship for TF-IDF / similarity matching"""
        parts = [
            self.title or '',
            self.domain or '',
            self.required_skills or '',
            self.description or '',
            self.responsibilities or '',
            self.eligibility or '',
        ]
        return " ".join(parts)


class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    internship_id = db.Column(db.Integer, db.ForeignKey('internships.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    status = db.Column(db.String(30), default='Applied', nullable=False) # 'Applied', 'Under Review', 'Shortlisted', 'Selected', 'Completed', 'Rejected'
    tfidf_score = db.Column(db.Float, default=0.0)      # Cosine similarity (0-100%)
    rf_probability = db.Column(db.Float, default=0.0)   # Random forest shortlist probability (0-100%)
    cover_letter = db.Column(db.Text)
    company_notes = db.Column(db.Text)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company_profiles.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    internship_id = db.Column(db.Integer, db.ForeignKey('internships.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False) # 1 to 5 overall
    work_environment_rating = db.Column(db.Integer, default=5)
    learning_rating = db.Column(db.Integer, default=5)
    mentor_support_rating = db.Column(db.Integer, default=5)
    title = db.Column(db.String(150), nullable=False)
    review_text = db.Column(db.Text, nullable=False)
    pros = db.Column(db.Text)
    cons = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(30), default='info') # 'info', 'success', 'warning', 'status'
    link = db.Column(db.String(200))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
