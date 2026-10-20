import os
import uuid
import json
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, Response
from db_mongo import (
    users_col, students_col, companies_col, internships_col,
    applications_col, reviews_col, notifications_col, MongoHelper, db, MONGO_URI
)
from ml_engine import calculate_tfidf_similarity, extract_skill_overlap, shortlist_predictor
from seed_mongo import seed_mongo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'internhub-super-secret-key-mongodb-2026'

# ----------------- Helper Decorators & Context ----------------- #
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login'))
            if session.get('role') not in roles:
                flash('Unauthorized access for your account type.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    if 'user_id' in session:
        user = MongoHelper.get_user_by_id(session['user_id'])
        if user:
            if user['role'] == 'student':
                user['student_profile'] = MongoHelper.get_student_by_user_id(user['id'])
            elif user['role'] == 'company':
                user['company_profile'] = MongoHelper.get_company_by_user_id(user['id'])
            return user
    return None

@app.context_processor
def inject_global_vars():
    user = get_current_user()
    unread_notifications_count = 0
    if user:
        unread_notifications_count = notifications_col.count_documents({
            'user_id': str(user['id']),
            'is_read': False
        })
    return dict(
        current_user=user,
        unread_notifications_count=unread_notifications_count,
        now=datetime.utcnow()
    )

def create_notification(user_id, title, message, category='info', link=None):
    try:
        notifications_col.insert_one({
            'user_id': str(user_id),
            'title': title,
            'message': message,
            'category': category,
            'link': link,
            'is_read': False,
            'created_at': datetime.utcnow()
        })
    except Exception as e:
        print(f"Error creating notification: {e}")

# ----------------- Public Routes ----------------- #
@app.route('/')
def index():
    featured_cursor = internships_col.find({'is_active': True}).sort('created_at', -1).limit(6)
    featured_internships = []
    for item in featured_cursor:
        item = MongoHelper.format_doc(item)
        item['company'] = MongoHelper.get_company_by_id(item['company_id'])
        featured_internships.append(item)

    companies_cursor = companies_col.find({'is_verified': True}).limit(8)
    companies = [MongoHelper.get_company_by_id(c['_id']) for c in companies_cursor]

    reviews_cursor = reviews_col.find().sort('created_at', -1).limit(4)
    latest_reviews = []
    for r in reviews_cursor:
        r = MongoHelper.format_doc(r)
        r['company'] = MongoHelper.get_company_by_id(r['company_id'])
        latest_reviews.append(r)

    total_internships = internships_col.count_documents({'is_active': True})
    total_students = students_col.count_documents({})
    total_companies = companies_col.count_documents({})

    return render_template('index.html',
                           featured_internships=featured_internships,
                           companies=companies,
                           latest_reviews=latest_reviews,
                           total_internships=total_internships,
                           total_students=total_students,
                           total_companies=total_companies)

@app.route('/internships')
def internships():
    search = request.args.get('search', '').strip()
    domain = request.args.get('domain', '').strip()
    work_mode = request.args.get('work_mode', '').strip()
    location = request.args.get('location', '').strip()
    stipend_type = request.args.get('stipend_type', '').strip() # 'paid', 'unpaid'

    query = {'is_active': True}
    if domain:
        query['domain'] = domain
    if work_mode:
        query['work_mode'] = work_mode
    if location:
        query['location'] = {'$regex': location, '$options': 'i'}
    if stipend_type == 'unpaid':
        query['stipend'] = {'$regex': 'unpaid|unstipended|free|0', '$options': 'i'}
    elif stipend_type == 'paid':
        query['stipend'] = {'$not': {'$regex': 'unpaid|unstipended', '$options': 'i'}}

    if search:
        query['$or'] = [
            {'title': {'$regex': search, '$options': 'i'}},
            {'required_skills': {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}}
        ]

    internship_list = []
    for item in internships_col.find(query).sort('created_at', -1):
        item = MongoHelper.format_doc(item)
        item['company'] = MongoHelper.get_company_by_id(item['company_id'])
        internship_list.append(item)

    domains = internships_col.distinct('domain')

    user = get_current_user()
    student_profile = user.get('student_profile') if (user and user.get('role') == 'student') else None

    scored_internships = []
    for item in internship_list:
        match_info = None
        has_applied = False
        if student_profile:
            match_info = shortlist_predictor.predict_shortlist_probability(student_profile, item)
            has_applied = applications_col.find_one({
                'internship_id': str(item['id']),
                'student_id': str(student_profile['id'])
            }) is not None

        scored_internships.append({
            'obj': item,
            'match': match_info,
            'has_applied': has_applied
        })

    return render_template('internships.html',
                           internships=scored_internships,
                           domains=domains,
                           selected_domain=domain,
                           selected_mode=work_mode,
                           selected_stipend_type=stipend_type,
                           search=search,
                           location=location)

@app.route('/internships/<internship_id>')
def internship_detail(internship_id):
    internship = MongoHelper.get_internship_by_id(internship_id)
    if not internship:
        flash('Internship position not found.', 'danger')
        return redirect(url_for('internships'))

    user = get_current_user()
    student_profile = user.get('student_profile') if (user and user.get('role') == 'student') else None

    existing_application = None
    match_info = None
    if student_profile:
        existing_application = applications_col.find_one({
            'internship_id': str(internship['id']),
            'student_id': str(student_profile['id'])
        })
        if existing_application:
            existing_application = MongoHelper.format_doc(existing_application)
        match_info = shortlist_predictor.predict_shortlist_probability(student_profile, internship)

    company_reviews = []
    for r in reviews_col.find({'company_id': str(internship['company_id'])}).sort('created_at', -1):
        company_reviews.append(MongoHelper.format_doc(r))

    return render_template('internship_detail.html',
                           internship=internship,
                           existing_application=existing_application,
                           match_info=match_info,
                           company_reviews=company_reviews)

@app.route('/reviews')
def reviews():
    company_id = request.args.get('company_id', '').strip()
    query = {}
    if company_id:
        query['company_id'] = str(company_id)

    all_reviews = []
    for r in reviews_col.find(query).sort('created_at', -1):
        r = MongoHelper.format_doc(r)
        r['company'] = MongoHelper.get_company_by_id(r['company_id'])
        all_reviews.append(r)

    companies = [MongoHelper.get_company_by_id(c['_id']) for c in companies_col.find()]

    return render_template('reviews.html', reviews=all_reviews, companies=companies, selected_company=company_id)

@app.route('/companies/<company_id>')
def company_detail(company_id):
    company = MongoHelper.get_company_by_id(company_id)
    if not company:
        flash('Company profile not found.', 'danger')
        return redirect(url_for('index'))

    active_internships = []
    for job in internships_col.find({'company_id': str(company['id']), 'is_active': True}):
        job = MongoHelper.format_doc(job)
        job['company'] = company
        active_internships.append(job)

    company_reviews = []
    for r in reviews_col.find({'company_id': str(company['id'])}).sort('created_at', -1):
        company_reviews.append(MongoHelper.format_doc(r))

    return render_template('company_detail.html',
                           company=company,
                           internships=active_internships,
                           reviews=company_reviews)

# ----------------- Authentication Routes ----------------- #
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect_user_dashboard(session.get('role'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = MongoHelper.get_user_by_email(email)
        if user and MongoHelper.check_password(user, password):
            session['user_id'] = str(user['id'])
            session['role'] = user['role']
            session['email'] = user['email']
            flash(f'Welcome back, {user["email"]}!', 'success')
            next_url = request.args.get('next')
            if next_url and not next_url.startswith('//'):
                return redirect(next_url)
            return redirect_user_dashboard(user['role'])
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('auth/login.html')

@app.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        full_name = request.form.get('full_name', '').strip()
        college_name = request.form.get('college_name', '').strip()
        department = request.form.get('department', '').strip()
        year_of_study = request.form.get('year_of_study', '').strip()
        cgpa = float(request.form.get('cgpa') or 0.0)
        technical_skills = request.form.get('technical_skills', '').strip()

        if MongoHelper.get_user_by_email(email):
            flash('Email already registered! Please log in.', 'warning')
            return redirect(url_for('login'))

        user = MongoHelper.create_user(email, password, 'student')

        student_doc = {
            'user_id': str(user['id']),
            'full_name': full_name,
            'college_name': college_name,
            'department': department,
            'year_of_study': year_of_study,
            'cgpa': cgpa,
            'technical_skills': technical_skills,
            'soft_skills': '',
            'bio': '',
            'location': '',
            'career_interests': '',
            'github_url': '',
            'linkedin_url': '',
            'portfolio_url': '',
            'educations': [],
            'experiences': [],
            'projects': [],
            'certifications': [],
            'updated_at': datetime.utcnow()
        }
        students_col.insert_one(student_doc)

        session['user_id'] = str(user['id'])
        session['role'] = 'student'
        session['email'] = user['email']

        create_notification(
            user['id'],
            "Welcome to InternHub! 🚀",
            "Complete your dynamic resume to receive high-accuracy AI internship recommendations.",
            category="success",
            link="/student/resume"
        )
        flash('Student account created! Start building your dynamic resume.', 'success')
        return redirect(url_for('student_resume'))

    return render_template('auth/register_student.html')

@app.route('/register/company', methods=['GET', 'POST'])
def register_company():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        company_name = request.form.get('company_name', '').strip()
        industry = request.form.get('industry', '').strip()
        location = request.form.get('location', '').strip()
        website = request.form.get('website', '').strip()
        contact_person = request.form.get('contact_person', '').strip()
        description = request.form.get('description', '').strip()

        if MongoHelper.get_user_by_email(email):
            flash('Email already registered! Please log in.', 'warning')
            return redirect(url_for('login'))

        user = MongoHelper.create_user(email, password, 'company')

        company_doc = {
            'user_id': str(user['id']),
            'company_name': company_name,
            'industry': industry,
            'location': location,
            'website': website,
            'contact_person': contact_person,
            'description': description,
            'is_verified': True,
            'logo': 'default-company.png',
            'created_at': datetime.utcnow()
        }
        companies_col.insert_one(company_doc)

        session['user_id'] = str(user['id'])
        session['role'] = 'company'
        session['email'] = user['email']

        create_notification(
            user['id'],
            "Welcome, Employer Partner! 🏢",
            "Post your first internship to begin receiving AI-ranked candidate applications.",
            category="success",
            link="/company/post-internship"
        )
        flash('Company registered! Post your first internship position.', 'success')
        return redirect(url_for('company_dashboard'))

    return render_template('auth/register_company.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out securely.', 'info')
    return redirect(url_for('index'))

def redirect_user_dashboard(role):
    if role == 'student':
        return redirect(url_for('student_dashboard'))
    elif role == 'company':
        return redirect(url_for('company_dashboard'))
    elif role == 'admin':
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('index'))

# ----------------- Student Routes ----------------- #
@app.route('/student/dashboard')
@role_required('student')
def student_dashboard():
    user = get_current_user()
    profile = user['student_profile']

    # Fetch active internships for AI recommendations
    all_internships = [MongoHelper.format_doc(i) for i in internships_col.find({'is_active': True})]
    for item in all_internships:
        item['company'] = MongoHelper.get_company_by_id(item['company_id'])

    applied_apps = list(applications_col.find({'student_id': str(profile['id'])}))
    applied_job_ids = [str(a['internship_id']) for a in applied_apps]

    recommendations = []
    for item in all_internships:
        if str(item['id']) in applied_job_ids:
            continue
        scores = shortlist_predictor.predict_shortlist_probability(profile, item)
        recommendations.append({
            'internship': item,
            'tfidf_score': scores['tfidf_score'],
            'rf_probability': scores['rf_probability'],
            'skill_overlap': scores['skill_overlap']
        })

    recommendations.sort(key=lambda x: (x['rf_probability'], x['tfidf_score']), reverse=True)
    top_recommendations = recommendations[:6]

    recent_applications = []
    for app_item in applications_col.find({'student_id': str(profile['id'])}).sort('applied_at', -1).limit(5):
        app_item = MongoHelper.format_doc(app_item)
        app_item['internship'] = MongoHelper.get_internship_by_id(app_item['internship_id'])
        recent_applications.append(app_item)

    return render_template('student/dashboard.html',
                           profile=profile,
                           recommendations=top_recommendations,
                           applications=recent_applications)

@app.route('/student/resume', methods=['GET', 'POST'])
@role_required('student')
def student_resume():
    user = get_current_user()
    profile = user['student_profile']

    if request.method == 'POST':
        update_data = {
            'full_name': request.form.get('full_name', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'college_name': request.form.get('college_name', '').strip(),
            'department': request.form.get('department', '').strip(),
            'year_of_study': request.form.get('year_of_study', '').strip(),
            'cgpa': float(request.form.get('cgpa') or 0.0),
            'location': request.form.get('location', '').strip(),
            'bio': request.form.get('bio', '').strip(),
            'career_interests': request.form.get('career_interests', '').strip(),
            'technical_skills': request.form.get('technical_skills', '').strip(),
            'soft_skills': request.form.get('soft_skills', '').strip(),
            'github_url': request.form.get('github_url', '').strip(),
            'linkedin_url': request.form.get('linkedin_url', '').strip(),
            'portfolio_url': request.form.get('portfolio_url', '').strip(),
            'updated_at': datetime.utcnow()
        }

        students_col.update_one({'_id': MongoHelper.to_id(profile['id'])}, {'$set': update_data})
        flash('Dynamic Resume profile updated successfully in MongoDB!', 'success')
        return redirect(url_for('student_resume'))

    return render_template('student/resume_builder.html', profile=profile)

@app.route('/student/resume/add-education', methods=['POST'])
@role_required('student')
def add_education():
    user = get_current_user()
    profile = user['student_profile']
    edu = {
        'id': str(uuid.uuid4())[:8],
        'degree': request.form.get('degree', '').strip(),
        'institution': request.form.get('institution', '').strip(),
        'field_of_study': request.form.get('field_of_study', '').strip(),
        'start_year': request.form.get('start_year', '').strip(),
        'end_year': request.form.get('end_year', '').strip(),
        'grade_or_cgpa': request.form.get('grade_or_cgpa', '').strip()
    }
    students_col.update_one({'_id': MongoHelper.to_id(profile['id'])}, {'$push': {'educations': edu}})
    flash('Education entry added!', 'success')
    return redirect(url_for('student_resume'))

@app.route('/student/resume/delete-education/<id>', methods=['POST'])
@role_required('student')
def delete_education(id):
    user = get_current_user()
    profile = user['student_profile']
    students_col.update_one({'_id': MongoHelper.to_id(profile['id'])}, {'$pull': {'educations': {'id': str(id)}}})
    flash('Education entry removed.', 'info')
    return redirect(url_for('student_resume'))

@app.route('/student/resume/add-experience', methods=['POST'])
@role_required('student')
def add_experience():
    user = get_current_user()
    profile = user['student_profile']
    exp = {
        'id': str(uuid.uuid4())[:8],
        'title': request.form.get('title', '').strip(),
        'company_name': request.form.get('company_name', '').strip(),
        'location': request.form.get('location', '').strip(),
        'start_date': request.form.get('start_date', '').strip(),
        'end_date': request.form.get('end_date', '').strip(),
        'is_current': bool(request.form.get('is_current')),
        'description': request.form.get('description', '').strip()
    }
    students_col.update_one({'_id': MongoHelper.to_id(profile['id'])}, {'$push': {'experiences': exp}})
    flash('Experience entry added!', 'success')
    return redirect(url_for('student_resume'))

@app.route('/student/resume/delete-experience/<id>', methods=['POST'])
@role_required('student')
def delete_experience(id):
    user = get_current_user()
    profile = user['student_profile']
    students_col.update_one({'_id': MongoHelper.to_id(profile['id'])}, {'$pull': {'experiences': {'id': str(id)}}})
    flash('Experience entry removed.', 'info')
    return redirect(url_for('student_resume'))

@app.route('/student/resume/add-project', methods=['POST'])
@role_required('student')
def add_project():
    user = get_current_user()
    profile = user['student_profile']
    proj = {
        'id': str(uuid.uuid4())[:8],
        'title': request.form.get('title', '').strip(),
        'technologies': request.form.get('technologies', '').strip(),
        'project_url': request.form.get('project_url', '').strip(),
        'description': request.form.get('description', '').strip()
    }
    students_col.update_one({'_id': MongoHelper.to_id(profile['id'])}, {'$push': {'projects': proj}})
    flash('Project entry added!', 'success')
    return redirect(url_for('student_resume'))

@app.route('/student/resume/delete-project/<id>', methods=['POST'])
@role_required('student')
def delete_project(id):
    user = get_current_user()
    profile = user['student_profile']
    students_col.update_one({'_id': MongoHelper.to_id(profile['id'])}, {'$pull': {'projects': {'id': str(id)}}})
    flash('Project entry removed.', 'info')
    return redirect(url_for('student_resume'))

@app.route('/student/resume/add-certification', methods=['POST'])
@role_required('student')
def add_certification():
    user = get_current_user()
    profile = user['student_profile']
    cert = {
        'id': str(uuid.uuid4())[:8],
        'title': request.form.get('title', '').strip(),
        'issuing_organization': request.form.get('issuing_organization', '').strip(),
        'issue_date': request.form.get('issue_date', '').strip(),
        'credential_url': request.form.get('credential_url', '').strip()
    }
    students_col.update_one({'_id': MongoHelper.to_id(profile['id'])}, {'$push': {'certifications': cert}})
    flash('Certification entry added!', 'success')
    return redirect(url_for('student_resume'))

@app.route('/student/resume/delete-certification/<id>', methods=['POST'])
@role_required('student')
def delete_certification(id):
    user = get_current_user()
    profile = user['student_profile']
    students_col.update_one({'_id': MongoHelper.to_id(profile['id'])}, {'$pull': {'certifications': {'id': str(id)}}})
    flash('Certification entry removed.', 'info')
    return redirect(url_for('student_resume'))

@app.route('/student/apply/<internship_id>', methods=['POST'])
@role_required('student')
def apply_internship(internship_id):
    internship = MongoHelper.get_internship_by_id(internship_id)
    if not internship:
        flash('Internship not found.', 'danger')
        return redirect(url_for('internships'))

    user = get_current_user()
    profile = user['student_profile']

    existing = applications_col.find_one({
        'internship_id': str(internship['id']),
        'student_id': str(profile['id'])
    })
    if existing:
        flash('You have already applied for this position.', 'info')
        return redirect(url_for('student_applications'))

    cover_letter = request.form.get('cover_letter', '').strip()

    pred = shortlist_predictor.predict_shortlist_probability(profile, internship)

    app_doc = {
        'internship_id': str(internship['id']),
        'student_id': str(profile['id']),
        'status': 'Applied',
        'tfidf_score': pred['tfidf_score'],
        'rf_probability': pred['rf_probability'],
        'cover_letter': cover_letter,
        'company_notes': '',
        'applied_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    applications_col.insert_one(app_doc)

    # Notify student
    create_notification(
        user['id'],
        "Application Submitted Successfully! 📄",
        f"Your application for {internship['title']} at {internship['company']['company_name']} was submitted with a {pred['tfidf_score']}% AI match score.",
        category="success",
        link="/student/applications"
    )

    # Notify company employer
    create_notification(
        internship['company']['user_id'],
        "New Internship Application Received 🎯",
        f"{profile['full_name']} applied for {internship['title']} (AI Match: {pred['tfidf_score']}%, Shortlist Odds: {pred['rf_probability']}%).",
        category="info",
        link="/company/applicants"
    )

    flash('Application submitted successfully! Track your status in your applications tab.', 'success')
    return redirect(url_for('student_applications'))

@app.route('/student/applications')
@role_required('student')
def student_applications():
    user = get_current_user()
    profile = user['student_profile']

    applications = []
    for a in applications_col.find({'student_id': str(profile['id'])}).sort('applied_at', -1):
        a = MongoHelper.format_doc(a)
        a['internship'] = MongoHelper.get_internship_by_id(a['internship_id'])
        applications.append(a)

    user_reviews = list(reviews_col.find({'student_id': str(profile['id'])}))
    reviewed_company_ids = [str(r['company_id']) for r in user_reviews]

    return render_template('student/applications.html',
                           applications=applications,
                           reviewed_company_ids=reviewed_company_ids)

@app.route('/student/review/<application_id>', methods=['GET', 'POST'])
@role_required('student')
def add_review(application_id):
    user = get_current_user()
    profile = user['student_profile']

    app_record = applications_col.find_one({
        '_id': MongoHelper.to_id(application_id),
        'student_id': str(profile['id'])
    })
    if not app_record:
        flash('Application record not found.', 'danger')
        return redirect(url_for('student_applications'))

    app_record = MongoHelper.format_doc(app_record)
    app_record['internship'] = MongoHelper.get_internship_by_id(app_record['internship_id'])

    # SECURITY & BUSINESS RULE CHECK: Must be 'Completed' to review!
    if app_record['status'] != 'Completed':
        flash('Permission Denied: You can only submit a company review after successfully completing your internship.', 'danger')
        return redirect(url_for('student_applications'))

    existing_review = reviews_col.find_one({
        'student_id': str(profile['id']),
        'internship_id': str(app_record['internship_id'])
    })
    if existing_review:
        flash('You have already submitted a review for this completed internship.', 'info')
        return redirect(url_for('reviews', company_id=app_record['internship']['company_id']))

    if request.method == 'POST':
        rating = int(request.form.get('rating', 5))
        env_rating = int(request.form.get('work_environment_rating', 5))
        learn_rating = int(request.form.get('learning_rating', 5))
        mentor_rating = int(request.form.get('mentor_support_rating', 5))
        title = request.form.get('title', '').strip()
        review_text = request.form.get('review_text', '').strip()
        pros = request.form.get('pros', '').strip()
        cons = request.form.get('cons', '').strip()

        review_doc = {
            'company_id': str(app_record['internship']['company_id']),
            'student_id': str(profile['id']),
            'internship_id': str(app_record['internship_id']),
            'rating': rating,
            'work_environment_rating': env_rating,
            'learning_rating': learn_rating,
            'mentor_support_rating': mentor_rating,
            'title': title,
            'review_text': review_text,
            'pros': pros,
            'cons': cons,
            'created_at': datetime.utcnow()
        }
        reviews_col.insert_one(review_doc)

        # Notify company
        create_notification(
            app_record['internship']['company']['user_id'],
            "New Verified Intern Review Received ⭐",
            f"A completed intern ({profile['full_name']}) has submitted a {rating}-star rating and feedback.",
            category="success",
            link="/company/reviews"
        )

        flash('Thank you! Your verified internship review has been stored in MongoDB.', 'success')
        return redirect(url_for('reviews', company_id=app_record['internship']['company_id']))

    return render_template('student/add_review.html', application=app_record)

@app.route('/student/notifications')
@login_required
def notifications():
    user = get_current_user()
    user_notifications = []
    for n in notifications_col.find({'user_id': str(user['id'])}).sort('created_at', -1):
        user_notifications.append(MongoHelper.format_doc(n))

    # Mark as read
    notifications_col.update_many({'user_id': str(user['id']), 'is_read': False}, {'$set': {'is_read': True}})

    return render_template('student/notifications.html', notifications=user_notifications)

# ----------------- Company Routes ----------------- #
@app.route('/company/dashboard')
@role_required('company')
def company_dashboard():
    user = get_current_user()
    company = user['company_profile']

    internships = []
    for job in internships_col.find({'company_id': str(company['id'])}):
        job = MongoHelper.format_doc(job)
        job['applications'] = list(applications_col.find({'internship_id': str(job['id'])}))
        internships.append(job)

    internship_ids = [str(i['id']) for i in internships]

    all_applicants = []
    if internship_ids:
        for app in applications_col.find({'internship_id': {'$in': internship_ids}}).sort('applied_at', -1):
            app = MongoHelper.format_doc(app)
            app['student'] = MongoHelper.format_doc(students_col.find_one({'_id': MongoHelper.to_id(app['student_id'])}))
            if app['student']:
                app['student']['user'] = MongoHelper.get_user_by_id(app['student']['user_id'])
            app['internship'] = MongoHelper.get_internship_by_id(app['internship_id'])
            all_applicants.append(app)

    total_listings = len(internships)
    total_applicants = len(all_applicants)
    shortlisted_count = sum(1 for a in all_applicants if a['status'] in ['Shortlisted', 'Selected', 'Completed'])

    recent_reviews = []
    for r in reviews_col.find({'company_id': str(company['id'])}).sort('created_at', -1).limit(3):
        recent_reviews.append(MongoHelper.format_doc(r))

    return render_template('company/dashboard.html',
                           company=company,
                           internships=internships[:4],
                           recent_applicants=all_applicants[:6],
                           total_listings=total_listings,
                           total_applicants=total_applicants,
                           shortlisted_count=shortlisted_count,
                           recent_reviews=recent_reviews)

@app.route('/company/post-internship', methods=['GET', 'POST'])
@role_required('company')
def post_internship():
    user = get_current_user()
    company = user['company_profile']

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        domain = request.form.get('domain', '').strip()
        required_skills = request.form.get('required_skills', '').strip()
        description = request.form.get('description', '').strip()
        responsibilities = request.form.get('responsibilities', '').strip()
        eligibility = request.form.get('eligibility', '').strip()
        min_cgpa = float(request.form.get('min_cgpa') or 0.0)
        stipend = request.form.get('stipend', '').strip()
        location = request.form.get('location', '').strip()
        work_mode = request.form.get('work_mode', 'Remote')
        duration_months = int(request.form.get('duration_months') or 3)
        vacancies = int(request.form.get('vacancies') or 1)
        deadline = request.form.get('deadline', '').strip()

        internship_doc = {
            'company_id': str(company['id']),
            'title': title,
            'domain': domain,
            'required_skills': required_skills,
            'description': description,
            'responsibilities': responsibilities,
            'eligibility': eligibility,
            'min_cgpa': min_cgpa,
            'stipend': stipend,
            'location': location,
            'work_mode': work_mode,
            'duration_months': duration_months,
            'vacancies': vacancies,
            'deadline': deadline,
            'is_active': True,
            'created_at': datetime.utcnow()
        }
        res = internships_col.insert_one(internship_doc)
        new_id = str(res.inserted_id)

        # Notify students whose skills match the new internship (TF-IDF >= 50%)
        for s in students_col.find():
            s = MongoHelper.format_doc(s)
            s_text = MongoHelper.get_student_resume_text(s)
            score = calculate_tfidf_similarity(s_text, MongoHelper.get_job_text(internship_doc), s.get('technical_skills', ''), required_skills)
            if score >= 50.0:
                create_notification(
                    s['user_id'],
                    "New Matching Internship Opportunity",
                    f"'{title}' at {company['company_name']} matches your dynamic resume ({score}% match). Apply now!",
                    category="info",
                    link=f"/internships/{new_id}"
                )

        flash('Internship posted successfully!', 'success')
        return redirect(url_for('manage_internships'))

    return render_template('company/post_internship.html', company=company)

@app.route('/company/manage-internships')
@role_required('company')
def manage_internships():
    user = get_current_user()
    company = user['company_profile']

    internships = []
    for job in internships_col.find({'company_id': str(company['id'])}).sort('created_at', -1):
        job = MongoHelper.format_doc(job)
        job['applications'] = list(applications_col.find({'internship_id': str(job['id'])}))
        internships.append(job)

    return render_template('company/manage_internships.html', internships=internships)

@app.route('/company/internship/<id>/toggle', methods=['POST'])
@role_required('company')
def toggle_internship(id):
    user = get_current_user()
    company = user['company_profile']

    job = internships_col.find_one({'_id': MongoHelper.to_id(id), 'company_id': str(company['id'])})
    if job:
        new_status = not job.get('is_active', True)
        internships_col.update_one({'_id': job['_id']}, {'$set': {'is_active': new_status}})
        flash(f"Internship status updated to {'Active' if new_status else 'Closed'}.", 'info')

    return redirect(url_for('manage_internships'))

@app.route('/company/applicants')
@role_required('company')
def company_applicants():
    user = get_current_user()
    company = user['company_profile']

    internship_id = request.args.get('internship_id', '').strip()
    status_filter = request.args.get('status', '').strip()
    sort_by = request.args.get('sort', 'tfidf').strip()

    company_internships = []
    for job in internships_col.find({'company_id': str(company['id'])}):
        job = MongoHelper.format_doc(job)
        job['applications'] = list(applications_col.find({'internship_id': str(job['id'])}))
        company_internships.append(job)

    internship_ids = [str(i['id']) for i in company_internships]

    if not internship_ids:
        return render_template('company/applicants.html', applicants=[], internships=[])

    query = {'internship_id': {'$in': internship_ids}}
    if internship_id:
        query['internship_id'] = str(internship_id)
    if status_filter:
        query['status'] = status_filter

    applicants = []
    for app in applications_col.find(query):
        app = MongoHelper.format_doc(app)
        app['student'] = MongoHelper.format_doc(students_col.find_one({'_id': MongoHelper.to_id(app['student_id'])}))
        if app['student']:
            app['student']['user'] = MongoHelper.get_user_by_id(app['student']['user_id'])
        app['internship'] = MongoHelper.get_internship_by_id(app['internship_id'])
        applicants.append(app)

    # Sort applicants
    if sort_by == 'tfidf':
        applicants.sort(key=lambda a: a.get('tfidf_score', 0.0), reverse=True)
    elif sort_by == 'rf':
        applicants.sort(key=lambda a: a.get('rf_probability', 0.0), reverse=True)
    elif sort_by == 'cgpa':
        applicants.sort(key=lambda a: float(a.get('student', {}).get('cgpa') or 0.0), reverse=True)
    else:
        applicants.sort(key=lambda a: a.get('applied_at', datetime.min), reverse=True)

    return render_template('company/applicants.html',
                           applicants=applicants,
                           internships=company_internships,
                           selected_internship=internship_id,
                           selected_status=status_filter,
                           selected_sort=sort_by)

@app.route('/company/applicant/<app_id>/status', methods=['POST'])
@role_required('company')
def update_applicant_status(app_id):
    user = get_current_user()
    company = user['company_profile']

    app_doc = applications_col.find_one({'_id': MongoHelper.to_id(app_id)})
    if not app_doc:
        flash('Applicant record not found.', 'danger')
        return redirect(url_for('company_applicants'))

    job = internships_col.find_one({'_id': MongoHelper.to_id(app_doc['internship_id'])})
    if not job or str(job['company_id']) != str(company['id']):
        flash('Unauthorized.', 'danger')
        return redirect(url_for('company_applicants'))

    new_status = request.form.get('status')
    notes = request.form.get('company_notes', '').strip()

    valid_statuses = ['Applied', 'Under Review', 'Shortlisted', 'Selected', 'Completed', 'Rejected']
    if new_status in valid_statuses:
        old_status = app_doc.get('status', 'Applied')
        update_data = {'status': new_status, 'updated_at': datetime.utcnow()}
        if notes:
            update_data['company_notes'] = notes
        applications_col.update_one({'_id': app_doc['_id']}, {'$set': update_data})

        student = students_col.find_one({'_id': MongoHelper.to_id(app_doc['student_id'])})
        if student:
            cat_map = {
                'Shortlisted': 'success',
                'Selected': 'success',
                'Completed': 'status',
                'Rejected': 'warning',
                'Under Review': 'info'
            }
            create_notification(
                student['user_id'],
                f"Application Status Updated: {new_status} 📢",
                f"Your application for {job['title']} at {company['company_name']} is now '{new_status}'.",
                category=cat_map.get(new_status, 'info'),
                link="/student/applications"
            )

        flash(f"Candidate status updated from '{old_status}' to '{new_status}'.", 'success')

    return redirect(request.referrer or url_for('company_applicants'))

@app.route('/company/applicant/<app_id>/resume')
@role_required('company', 'admin')
def view_candidate_resume(app_id):
    application = MongoHelper.format_doc(applications_col.find_one({'_id': MongoHelper.to_id(app_id)}))
    if not application:
        flash('Application not found.', 'danger')
        return redirect(url_for('company_applicants'))

    student = MongoHelper.format_doc(students_col.find_one({'_id': MongoHelper.to_id(application['student_id'])}))
    student['user'] = MongoHelper.get_user_by_id(student['user_id'])
    internship = MongoHelper.get_internship_by_id(application['internship_id'])

    match_details = shortlist_predictor.predict_shortlist_probability(student, internship)

    return render_template('company/view_resume.html',
                           application=application,
                           student=student,
                           internship=internship,
                           match_details=match_details)

@app.route('/company/reviews')
@role_required('company')
def company_reviews():
    user = get_current_user()
    company = user['company_profile']

    reviews_list = []
    for r in reviews_col.find({'company_id': str(company['id'])}).sort('created_at', -1):
        reviews_list.append(MongoHelper.format_doc(r))

    return render_template('company/reviews.html', company=company, reviews=reviews_list)

# ----------------- Admin Routes ----------------- #
@app.route('/admin/dashboard')
@role_required('admin')
def admin_dashboard():
    total_students = students_col.count_documents({})
    total_companies = companies_col.count_documents({})
    total_internships = internships_col.count_documents({})
    total_applications = applications_col.count_documents({})
    total_reviews = reviews_col.count_documents({})

    # 1. Companies
    companies = [MongoHelper.get_company_by_id(c['_id']) for c in companies_col.find()]
    for c in companies:
        c['user'] = MongoHelper.get_user_by_id(c['user_id'])
        c['internships'] = list(internships_col.find({'company_id': str(c['id'])}))

    # 2. Registered Students
    students = [MongoHelper.format_doc(s) for s in students_col.find().sort('updated_at', -1)]
    for s in students:
        s['user'] = MongoHelper.get_user_by_id(s['user_id'])
        s['applications_count'] = applications_col.count_documents({'student_id': str(s['id'])})

    # 3. All Internships
    all_internships = [MongoHelper.format_doc(i) for i in internships_col.find().sort('created_at', -1)]
    for i in all_internships:
        i['company'] = MongoHelper.get_company_by_id(i['company_id'])
        i['applications_count'] = applications_col.count_documents({'internship_id': str(i['id'])})

    # 4. All Applications Process
    all_applications = [MongoHelper.format_doc(a) for a in applications_col.find().sort('applied_at', -1)]
    for a in all_applications:
        a['student'] = MongoHelper.format_doc(students_col.find_one({'_id': MongoHelper.to_id(a['student_id'])}))
        if a['student']:
            a['student']['user'] = MongoHelper.get_user_by_id(a['student']['user_id'])
        a['internship'] = MongoHelper.get_internship_by_id(a['internship_id'])

    # 5. Verified Reviews
    all_reviews = [MongoHelper.format_doc(r) for r in reviews_col.find().sort('created_at', -1)]
    for r in all_reviews:
        r['company'] = MongoHelper.get_company_by_id(r['company_id'])
        r['student'] = MongoHelper.format_doc(students_col.find_one({'_id': MongoHelper.to_id(r['student_id'])}))

    return render_template('admin/dashboard.html',
                           total_students=total_students,
                           total_companies=total_companies,
                           total_internships=total_internships,
                           total_applications=total_applications,
                           total_reviews=total_reviews,
                           companies=companies,
                           students=students,
                           internships=all_internships,
                           applications=all_applications,
                           reviews=all_reviews)

@app.route('/admin/company/<id>/verify', methods=['POST'])
@role_required('admin')
def toggle_company_verification(id):
    company = companies_col.find_one({'_id': MongoHelper.to_id(id)})
    if company:
        new_val = not company.get('is_verified', True)
        companies_col.update_one({'_id': company['_id']}, {'$set': {'is_verified': new_val}})
        flash(f"Company '{company.get('company_name')}' verification set to {new_val}.", 'info')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/internship/<id>/toggle', methods=['POST'])
@role_required('admin')
def admin_toggle_internship(id):
    job = internships_col.find_one({'_id': MongoHelper.to_id(id)})
    if job:
        new_status = not job.get('is_active', True)
        internships_col.update_one({'_id': job['_id']}, {'$set': {'is_active': new_status}})
        flash(f"Internship '{job.get('title')}' status updated to {'Active' if new_status else 'Closed'}.", 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/company/<id>/delete', methods=['POST'])
@role_required('admin')
def admin_delete_company(id):
    company = companies_col.find_one({'_id': MongoHelper.to_id(id)})
    if company:
        cid_str = str(company['_id'])
        cname = company.get('company_name', 'Company')
        user_id = company.get('user_id')

        # Find all internships for this company
        internships = list(internships_col.find({'company_id': cid_str}))
        internship_ids = [str(i['_id']) for i in internships]

        # Delete associated applications
        if internship_ids:
            applications_col.delete_many({'internship_id': {'$in': internship_ids}})

        # Delete associated reviews
        reviews_col.delete_many({'company_id': cid_str})

        # Delete internships
        internships_col.delete_many({'company_id': cid_str})

        # Delete company profile
        companies_col.delete_one({'_id': company['_id']})

        # Delete associated user account & notifications
        if user_id:
            users_col.delete_one({'_id': MongoHelper.to_id(user_id)})
            notifications_col.delete_many({'user_id': str(user_id)})

        flash(f"Company '{cname}' and all associated postings and applications were deleted successfully.", 'success')
    else:
        flash("Company record not found.", 'danger')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/student/<id>/delete', methods=['POST'])
@role_required('admin')
def admin_delete_student(id):
    student = students_col.find_one({'_id': MongoHelper.to_id(id)})
    if student:
        sid_str = str(student['_id'])
        sname = student.get('full_name', 'Student')
        user_id = student.get('user_id')

        # Delete applications submitted by this student
        applications_col.delete_many({'student_id': sid_str})

        # Delete reviews submitted by this student
        reviews_col.delete_many({'student_id': sid_str})

        # Delete student profile
        students_col.delete_one({'_id': student['_id']})

        # Delete user account & notifications
        if user_id:
            users_col.delete_one({'_id': MongoHelper.to_id(user_id)})
            notifications_col.delete_many({'user_id': str(user_id)})

        flash(f"Student '{sname}' and all associated application history were deleted successfully.", 'success')
    else:
        flash("Student record not found.", 'danger')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/application/<id>/delete', methods=['POST'])
@role_required('admin')
def admin_delete_application(id):
    app_doc = applications_col.find_one({'_id': MongoHelper.to_id(id)})
    if app_doc:
        applications_col.delete_one({'_id': app_doc['_id']})
        flash("Application record was deleted successfully.", 'success')
    else:
        flash("Application record not found.", 'danger')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/internship/<id>/delete', methods=['POST'])
@role_required('admin')
def admin_delete_internship(id):
    job = internships_col.find_one({'_id': MongoHelper.to_id(id)})
    if job:
        jid_str = str(job['_id'])
        jtitle = job.get('title', 'Internship')

        # Delete applications for this internship
        applications_col.delete_many({'internship_id': jid_str})

        # Delete internship
        internships_col.delete_one({'_id': job['_id']})
        flash(f"Internship '{jtitle}' and its applicant records were deleted successfully.", 'success')
    else:
        flash("Internship record not found.", 'danger')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/review/<id>/delete', methods=['POST'])
@role_required('admin')
def admin_delete_review(id):
    reviews_col.delete_one({'_id': MongoHelper.to_id(id)})
    flash('Review removed successfully.', 'info')
    return redirect(url_for('admin_dashboard'))

# ----------------- Visual Database Viewer ----------------- #
@app.route('/db-viewer')
@app.route('/admin/database')
def db_viewer():
    collection_name = request.args.get('collection', 'students').strip()
    search_q = request.args.get('q', '').strip()
    view_mode = request.args.get('mode', 'table').strip()

    all_collections = sorted(db.list_collection_names())
    if collection_name not in all_collections and all_collections:
        collection_name = all_collections[0]

    collection_stats = []
    total_docs = 0
    for col in all_collections:
        c_count = db[col].count_documents({})
        total_docs += c_count
        collection_stats.append({
            'name': col,
            'count': c_count,
            'is_active': (col == collection_name)
        })

    col_ref = db[collection_name]
    query = {}
    if search_q:
        try:
            from bson import ObjectId
            query = {'_id': ObjectId(search_q)}
        except Exception:
            sample = col_ref.find_one() or {}
            string_fields = [k for k, v in sample.items() if isinstance(v, str)]
            if string_fields:
                query = {'$or': [{f: {'$regex': search_q, '$options': 'i'}} for f in string_fields[:5]]}

    raw_docs = list(col_ref.find(query).limit(100))

    priority_keys = ['_id', 'full_name', 'email', 'title', 'company_name', 'role', 'status', 'domain', 'cgpa', 'rating', 'applied_at', 'created_at']
    all_keys = []
    seen_keys = set()
    for doc in raw_docs:
        for k in doc.keys():
            if k not in seen_keys:
                seen_keys.add(k)
                all_keys.append(k)

    ordered_keys = [k for k in priority_keys if k in seen_keys] + [k for k in all_keys if k not in priority_keys]

    formatted_docs = []
    for doc in raw_docs:
        doc_id = str(doc.get('_id'))
        json_repr = json.dumps(doc, indent=2, default=str, ensure_ascii=False)
        formatted_docs.append({
            'id': doc_id,
            'raw': doc,
            'json': json_repr
        })

    collection_json = json.dumps(raw_docs, indent=2, default=str, ensure_ascii=False)

    return render_template('admin/db_viewer.html',
                           collections=collection_stats,
                           current_collection=collection_name,
                           columns=ordered_keys,
                           documents=formatted_docs,
                           collection_json=collection_json,
                           total_db_docs=total_docs,
                           search_q=search_q,
                           view_mode=view_mode,
                           mongo_uri=MONGO_URI)

@app.route('/db-viewer/export/<collection>')
def export_collection(collection):
    if collection in db.list_collection_names():
        docs = list(db[collection].find())
        content = json.dumps(docs, indent=2, default=str, ensure_ascii=False)
        return Response(content,
                        mimetype='application/json',
                        headers={'Content-Disposition': f'attachment;filename={collection}_export.json'})
    return "Collection not found", 404

# ----------------- Startup Initialization ----------------- #
seed_mongo()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1']
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
