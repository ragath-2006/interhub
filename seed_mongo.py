from datetime import datetime, timedelta
from db_mongo import (
    users_col, students_col, companies_col, internships_col,
    applications_col, reviews_col, notifications_col, MongoHelper
)
from ml_engine import shortlist_predictor

def seed_mongo():
    if users_col.count_documents({}) > 0:
        return

    print("Seeding MongoDB with comprehensive sample data...")

    # 1. ADMIN
    admin_user = MongoHelper.create_user('admin@internhub.com', 'admin123', 'admin')

    # 2. COMPANIES
    # Google
    c1_user = MongoHelper.create_user('hr@google.com', 'company123', 'company')
    c1 = {
        'user_id': str(c1_user['id']),
        'company_name': "Google India Tech",
        'industry': "Software & AI",
        'website': "https://careers.google.com",
        'location': "Bengaluru, Karnataka",
        'description': "Google's mission is to organize the world's information and make it universally accessible and useful. We build products that help billions of users.",
        'contact_person': "Ananya Rao (Tech Talent Lead)",
        'phone': "+91 9876543210",
        'is_verified': True,
        'logo': "google-logo.png",
        'created_at': datetime.utcnow()
    }
    c1_id = companies_col.insert_one(c1).inserted_id

    # Microsoft
    c2_user = MongoHelper.create_user('talent@microsoft.com', 'company123', 'company')
    c2 = {
        'user_id': str(c2_user['id']),
        'company_name': "Microsoft IDC",
        'industry': "Cloud & Enterprise Software",
        'website': "https://careers.microsoft.com",
        'location': "Hyderabad, Telangana",
        'description': "Microsoft enables digital transformation for the era of an intelligent cloud and an intelligent edge. Join our Azure and Developer tools teams.",
        'contact_person': "Vikram Malhotra (Campus Recruitment)",
        'phone': "+91 9876543211",
        'is_verified': True,
        'logo': "microsoft-logo.png",
        'created_at': datetime.utcnow()
    }
    c2_id = companies_col.insert_one(c2).inserted_id

    # Swiggy
    c3_user = MongoHelper.create_user('careers@swiggy.in', 'company123', 'company')
    c3 = {
        'user_id': str(c3_user['id']),
        'company_name': "Swiggy Engineering",
        'industry': "E-Commerce & Food Tech",
        'website': "https://swiggy.careers",
        'location': "Bengaluru, Karnataka",
        'description': "Swiggy is India's leading on-demand convenience platform. We solve high-scale hyper-local logistics and real-time dispatch systems.",
        'contact_person': "Kavita Reddy (HR Manager)",
        'phone': "+91 9876543212",
        'is_verified': True,
        'logo': "swiggy-logo.png",
        'created_at': datetime.utcnow()
    }
    c3_id = companies_col.insert_one(c3).inserted_id

    # 3. INTERNSHIPS
    i1 = {
        'company_id': str(c1_id),
        'title': "AI & Machine Learning Research Intern",
        'domain': "Artificial Intelligence",
        'description': "We are seeking passionate AI/ML Interns to contribute to large language model optimizations, computer vision algorithms, and real-time inference systems. You will work alongside world-class research scientists.",
        'required_skills': "Python, Machine Learning, Deep Learning, PyTorch, TensorFlow, Scikit-Learn, NLP, Data Structures",
        'responsibilities': "1. Build and fine-tune ML predictive models.\n2. Analyze high-dimensional datasets.\n3. Implement TF-IDF, embeddings, and transformer pipelines.\n4. Collaborate on research papers and deployment pipelines.",
        'eligibility': "B.Tech/M.Tech in CS, AI, or Data Science with CGPA >= 8.0. Hands-on ML project experience required.",
        'min_cgpa': 8.0,
        'stipend': "₹45,000 / month",
        'location': "Bengaluru (Hybrid)",
        'work_mode': "Hybrid",
        'duration_months': 6,
        'vacancies': 3,
        'deadline': (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d"),
        'is_active': True,
        'created_at': datetime.utcnow()
    }
    i1_id = internships_col.insert_one(i1).inserted_id

    i2 = {
        'company_id': str(c2_id),
        'title': "Full Stack Software Engineer Intern",
        'domain': "Software Development",
        'description': "Join Microsoft Azure Cloud team to build scalable microservices and intuitive developer dashboard interfaces using modern web frameworks.",
        'required_skills': "Python, React, TypeScript, Node.js, REST APIs, SQL, Docker, Git, Cloud Computing",
        'responsibilities': "1. Design modular frontend components in React.\n2. Build RESTful APIs with Python/Node.\n3. Integrate relational databases and cloud caching.\n4. Write unit and integration test suites.",
        'eligibility': "Pre-final or Final year students in CSE/IT/ECE with strong programming fundamentals.",
        'min_cgpa': 7.5,
        'stipend': "₹40,000 / month",
        'location': "Hyderabad / Remote",
        'work_mode': "Remote",
        'duration_months': 3,
        'vacancies': 5,
        'deadline': (datetime.utcnow() + timedelta(days=25)).strftime("%Y-%m-%d"),
        'is_active': True,
        'created_at': datetime.utcnow()
    }
    i2_id = internships_col.insert_one(i2).inserted_id

    i3 = {
        'company_id': str(c3_id),
        'title': "Backend Systems Intern (Python / Flask / SQL)",
        'domain': "Backend Engineering",
        'description': "Help us scale high-throughput order fulfillment systems processing millions of concurrent transactions per day.",
        'required_skills': "Python, Flask, Django, PostgreSQL, Redis, Microservices, System Design, Algorithms",
        'responsibilities': "1. Build low-latency API endpoints.\n2. Optimize complex SQL queries and indexing.\n3. Implement caching and async task queues.\n4. Monitor system health and performance metrics.",
        'eligibility': "Engineering students proficient in Python backend frameworks and relational databases.",
        'min_cgpa': 7.0,
        'stipend': "₹35,000 / month",
        'location': "Bengaluru",
        'work_mode': "On-site",
        'duration_months': 6,
        'vacancies': 2,
        'deadline': (datetime.utcnow() + timedelta(days=15)).strftime("%Y-%m-%d"),
        'is_active': True,
        'created_at': datetime.utcnow()
    }
    i3_id = internships_col.insert_one(i3).inserted_id

    # Unpaid / Unstipended Community Open Source Internship
    i4 = {
        'company_id': str(c1_id),
        'title': "Open Source AI & Documentation Trainee",
        'domain': "Artificial Intelligence",
        'description': "Contribute to open source machine learning tutorials, example notebooks, and community documentation. Receive formal certificate of completion and 1-on-1 mentorship.",
        'required_skills': "Python, Git, Markdown, Technical Writing, Machine Learning Basics",
        'responsibilities': "1. Review and test Jupyter tutorial notebooks.\n2. Improve open source library documentation.\n3. Participate in bi-weekly open-source mentor office hours.",
        'eligibility': "Open to all students eager to gain practical open-source project experience.",
        'min_cgpa': 6.0,
        'stipend': "Unpaid / Unstipended (Certificate & Mentorship)",
        'location': "Remote",
        'work_mode': "Remote",
        'duration_months': 2,
        'vacancies': 10,
        'deadline': (datetime.utcnow() + timedelta(days=45)).strftime("%Y-%m-%d"),
        'is_active': True,
        'created_at': datetime.utcnow()
    }
    internships_col.insert_one(i4)

    # 4. STUDENTS (Dynamic Resumes)
    # Rahul Sharma
    s1_user = MongoHelper.create_user('student@internhub.com', 'student123', 'student')
    s1 = {
        'user_id': str(s1_user['id']),
        'full_name': "Rahul Sharma",
        'phone': "+91 9123456780",
        'college_name': "National Institute of Technology (NIT)",
        'department': "Computer Science & Engineering",
        'year_of_study': "3rd Year (6th Semester)",
        'cgpa': 8.85,
        'bio': "Passionate Full Stack Developer and Machine Learning enthusiast with hands-on experience building scalable web applications and intelligent data recommendation systems. Eager to solve real-world industry challenges.",
        'location': "Bengaluru, Karnataka",
        'career_interests': "Full Stack Engineering, Machine Learning, Cloud Architecture",
        'technical_skills': "Python, Flask, React, JavaScript, SQL, Machine Learning, Git, REST APIs, HTML/CSS, Docker",
        'soft_skills': "Problem Solving, Team Leadership, Technical Writing, Agile Collaboration",
        'github_url': "https://github.com/rahulsharma-demo",
        'linkedin_url': "https://linkedin.com/in/rahulsharma-demo",
        'portfolio_url': "https://rahulsharma.dev",
        'avatar': "default-avatar.png",
        'educations': [
            {
                'id': '1',
                'degree': "B.Tech in Computer Science and Engineering",
                'institution': "National Institute of Technology (NIT)",
                'field_of_study': "Computer Science",
                'start_year': "2023",
                'end_year': "2027",
                'grade_or_cgpa': "8.85 / 10.0"
            },
            {
                'id': '2',
                'degree': "Higher Secondary Certificate (Class XII)",
                'institution': "Delhi Public School",
                'field_of_study': "Science (PCM + CS)",
                'start_year': "2021",
                'end_year': "2023",
                'grade_or_cgpa': "95.4%"
            }
        ],
        'experiences': [
            {
                'id': '1',
                'title': "Summer Software Engineering Intern",
                'company_name': "Swiggy Engineering",
                'location': "Bengaluru",
                'start_date': "May 2025",
                'end_date': "July 2025",
                'is_current': False,
                'description': "Engineered REST API endpoints in Python Flask for restaurant menu parsing and reduced query response times by 35% through database index optimizations."
            }
        ],
        'projects': [
            {
                'id': '1',
                'title': "AI Career & Internship Recommendation Engine",
                'technologies': "Python, Flask, Machine Learning, Data Analytics, React",
                'project_url': "https://github.com/rahulsharma-demo/internhub-ai",
                'description': "Designed and deployed an intelligent matching algorithm comparing student resume vector embeddings with job specs using candidate matchmaking and ranking algorithms."
            },
            {
                'id': '2',
                'title': "E-Commerce Microservices Platform",
                'technologies': "Python, Docker, Redis, MongoDB, React.js",
                'project_url': "https://github.com/rahulsharma-demo/ecommerce-microservices",
                'description': "Architected containerized microservices handling authentication, product catalog, payment webhooks, and asynchronous order processing."
            }
        ],
        'certifications': [
            {
                'id': '1',
                'title': "Machine Learning Specialization",
                'issuing_organization': "DeepLearning.AI / Coursera",
                'issue_date': "Nov 2025",
                'credential_url': "https://coursera.org/verify/ML-SPECIALIZATION-RAHUL"
            },
            {
                'id': '2',
                'title': "AWS Certified Cloud Practitioner",
                'issuing_organization': "Amazon Web Services",
                'issue_date': "Jan 2026",
                'credential_url': "https://aws.amazon.com/verification/AWS-CP-RAHUL"
            }
        ],
        'updated_at': datetime.utcnow()
    }
    s1_id = students_col.insert_one(s1).inserted_id
    s1['id'] = str(s1_id)

    # 5. APPLICATIONS
    # Application 1: Completed at Swiggy (Allows verified review)
    pred1 = shortlist_predictor.predict_shortlist_probability(s1, i3)
    app1 = {
        'internship_id': str(i3_id),
        'student_id': str(s1_id),
        'status': "Completed",
        'tfidf_score': pred1['tfidf_score'],
        'rf_probability': pred1['rf_probability'],
        'cover_letter': "I have extensive experience in Python backend development, Flask, and database indexing.",
        'company_notes': "Successfully completed 6-month internship with outstanding ratings from team lead.",
        'applied_at': datetime.utcnow() - timedelta(days=90),
        'updated_at': datetime.utcnow() - timedelta(days=5)
    }
    applications_col.insert_one(app1)

    # Application 2: Shortlisted at Google
    pred2 = shortlist_predictor.predict_shortlist_probability(s1, i1)
    app2 = {
        'internship_id': str(i1_id),
        'student_id': str(s1_id),
        'status': "Shortlisted",
        'tfidf_score': pred2['tfidf_score'],
        'rf_probability': pred2['rf_probability'],
        'cover_letter': "My projects in TF-IDF recommendation systems make me an ideal fit.",
        'company_notes': "High AI match score and strong CGPA. Schedule round 1 interview.",
        'applied_at': datetime.utcnow() - timedelta(days=10),
        'updated_at': datetime.utcnow() - timedelta(days=2)
    }
    applications_col.insert_one(app2)

    # 6. REVIEWS
    rev1 = {
        'company_id': str(c3_id),
        'student_id': str(s1_id),
        'internship_id': str(i3_id),
        'rating': 5,
        'work_environment_rating': 5,
        'learning_rating': 5,
        'mentor_support_rating': 5,
        'title': "Incredible mentorship and massive scale engineering!",
        'review_text': "My 6-month internship at Swiggy was an eye-opening journey. I got the chance to work directly on high-concurrency order systems, receive code reviews from principal architects, and optimize live production databases.",
        'pros': "Great learning curve, supportive mentors, flexible remote options, high stipend.",
        'cons': "Can get fast-paced during festival demand peaks, but very rewarding.",
        'created_at': datetime.utcnow() - timedelta(days=4)
    }
    reviews_col.insert_one(rev1)

    # 7. NOTIFICATIONS
    notif1 = {
        'user_id': str(s1_user['id']),
        'title': "Application Shortlisted! 🎉",
        'message': "Congratulations! Google India Tech has shortlisted your application for AI & Machine Learning Research Intern.",
        'category': "success",
        'link': "/student/applications",
        'is_read': False,
        'created_at': datetime.utcnow() - timedelta(days=2)
    }
    notif2 = {
        'user_id': str(s1_user['id']),
        'title': "Internship Completed ✨",
        'message': "Your internship at Swiggy Engineering is marked as Completed. You are now verified to write an official company review.",
        'category': "status",
        'link': "/student/applications",
        'is_read': True,
        'created_at': datetime.utcnow() - timedelta(days=5)
    }
    notifications_col.insert_many([notif1, notif2])

    print("MongoDB seed completed successfully!")
