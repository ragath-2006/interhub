from datetime import datetime, timedelta
from models import db, User, StudentProfile, Education, Experience, Project, Certification, CompanyProfile, Internship, Application, Review, Notification
from ml_engine import shortlist_predictor

def seed_database():
    # Only seed if database is empty
    if User.query.first():
        return

    print("Seeding database with sample users, companies, internships, resumes, and reviews...")

    # 1. ADMIN USER
    admin_user = User(email='admin@internhub.com', role='admin')
    admin_user.set_password('admin123')
    db.session.add(admin_user)

    # 2. COMPANY USERS & PROFILES
    # Company 1: Google Cloud & AI
    c1_user = User(email='hr@google.com', role='company')
    c1_user.set_password('company123')
    db.session.add(c1_user)
    db.session.flush()

    c1_profile = CompanyProfile(
        user_id=c1_user.id,
        company_name="Google India Tech",
        industry="Software & AI",
        website="https://careers.google.com",
        location="Bengaluru, Karnataka",
        description="Google's mission is to organize the world's information and make it universally accessible and useful. We build products that help billions of users.",
        contact_person="Ananya Rao (Tech Talent Lead)",
        phone="+91 9876543210",
        is_verified=True,
        logo="google-logo.png"
    )
    db.session.add(c1_profile)

    # Company 2: Microsoft Technologies
    c2_user = User(email='talent@microsoft.com', role='company')
    c2_user.set_password('company123')
    db.session.add(c2_user)
    db.session.flush()

    c2_profile = CompanyProfile(
        user_id=c2_user.id,
        company_name="Microsoft IDC",
        industry="Cloud & Enterprise Software",
        website="https://careers.microsoft.com",
        location="Hyderabad, Telangana",
        description="Microsoft enables digital transformation for the era of an intelligent cloud and an intelligent edge. Join our Azure and Developer tools teams.",
        contact_person="Vikram Malhotra (Campus Recruitment)",
        phone="+91 9876543211",
        is_verified=True,
        logo="microsoft-logo.png"
    )
    db.session.add(c2_profile)

    # Company 3: Swiggy Engineering
    c3_user = User(email='careers@swiggy.in', role='company')
    c3_user.set_password('company123')
    db.session.add(c3_user)
    db.session.flush()

    c3_profile = CompanyProfile(
        user_id=c3_user.id,
        company_name="Swiggy Engineering",
        industry="E-Commerce & Food Tech",
        website="https://swiggy.careers",
        location="Bengaluru, Karnataka",
        description="Swiggy is India's leading on-demand convenience platform. We solve high-scale hyper-local logistics and real-time dispatch systems.",
        contact_person="Kavita Reddy (HR Manager)",
        phone="+91 9876543212",
        is_verified=True,
        logo="swiggy-logo.png"
    )
    db.session.add(c3_profile)

    # Company 4: Infosys Labs
    c4_user = User(email='jobs@infosys.com', role='company')
    c4_user.set_password('company123')
    db.session.add(c4_user)
    db.session.flush()

    c4_profile = CompanyProfile(
        user_id=c4_user.id,
        company_name="Infosys Innovation Labs",
        industry="Information Technology & Consulting",
        website="https://www.infosys.com",
        location="Pune, Maharashtra",
        description="A global leader in next-generation digital services and consulting. We navigate clients' digital transformation in 56+ countries.",
        contact_person="Sunil Deshmukh (Talent Acquisition)",
        phone="+91 9876543213",
        is_verified=True,
        logo="infosys-logo.png"
    )
    db.session.add(c4_profile)
    db.session.flush()

    # 3. INTERNSHIPS
    internship1 = Internship(
        company_id=c1_profile.id,
        title="AI & Machine Learning Research Intern",
        domain="Artificial Intelligence",
        description="We are seeking passionate AI/ML Interns to contribute to large language model optimizations, computer vision algorithms, and real-time inference systems. You will work alongside world-class research scientists.",
        required_skills="Python, Machine Learning, Deep Learning, PyTorch, TensorFlow, Scikit-Learn, NLP, Data Structures",
        responsibilities="1. Build and fine-tune ML predictive models.\n2. Analyze high-dimensional datasets.\n3. Implement TF-IDF, embeddings, and transformer pipelines.\n4. Collaborate on research papers and deployment pipelines.",
        eligibility="B.Tech/M.Tech in CS, AI, or Data Science with CGPA >= 8.0. Hands-on ML project experience required.",
        min_cgpa=8.0,
        stipend="₹45,000 / month",
        location="Bengaluru (Hybrid)",
        work_mode="Hybrid",
        duration_months=6,
        vacancies=3,
        deadline=(datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d"),
        is_active=True
    )
    db.session.add(internship1)

    internship2 = Internship(
        company_id=c2_profile.id,
        title="Full Stack Software Engineer Intern",
        domain="Software Development",
        description="Join Microsoft Azure Cloud team to build scalable microservices and intuitive developer dashboard interfaces using modern web frameworks.",
        required_skills="Python, React, TypeScript, Node.js, REST APIs, SQL, Docker, Git, Cloud Computing",
        responsibilities="1. Design modular frontend components in React.\n2. Build RESTful APIs with Python/Node.\n3. Integrate relational databases and cloud caching.\n4. Write unit and integration test suites.",
        eligibility="Pre-final or Final year students in CSE/IT/ECE with strong programming fundamentals.",
        min_cgpa=7.5,
        stipend="₹40,000 / month",
        location="Hyderabad / Remote",
        work_mode="Remote",
        duration_months=3,
        vacancies=5,
        deadline=(datetime.utcnow() + timedelta(days=25)).strftime("%Y-%m-%d"),
        is_active=True
    )
    db.session.add(internship2)

    internship3 = Internship(
        company_id=c3_profile.id,
        title="Backend Systems Intern (Python / Flask / SQL)",
        domain="Backend Engineering",
        description="Help us scale high-throughput order fulfillment systems processing millions of concurrent transactions per day.",
        required_skills="Python, Flask, Django, PostgreSQL, Redis, Microservices, System Design, Algorithms",
        responsibilities="1. Build low-latency API endpoints.\n2. Optimize complex SQL queries and indexing.\n3. Implement caching and async task queues.\n4. Monitor system health and performance metrics.",
        eligibility="Engineering students proficient in Python backend frameworks and relational databases.",
        min_cgpa=7.0,
        stipend="₹35,000 / month",
        location="Bengaluru",
        work_mode="On-site",
        duration_months=6,
        vacancies=2,
        deadline=(datetime.utcnow() + timedelta(days=15)).strftime("%Y-%m-%d"),
        is_active=True
    )
    db.session.add(internship3)

    internship4 = Internship(
        company_id=c3_profile.id,
        title="Data Analyst & Business Intelligence Intern",
        domain="Data Analytics",
        description="Work with customer conversion data, delivery heatmaps, and merchant metrics to provide actionable insights to executive leadership.",
        required_skills="SQL, Python, Pandas, PowerBI, Tableau, Excel, Statistical Analysis, Data Visualization",
        responsibilities="1. Write advanced SQL queries for analytics dashboards.\n2. Perform exploratory data analysis (EDA).\n3. Create executive reporting dashboards.\n4. Present findings to product managers.",
        eligibility="Open to all engineering, mathematics, and statistics undergraduates.",
        min_cgpa=7.0,
        stipend="₹30,000 / month",
        location="Bengaluru / Remote",
        work_mode="Hybrid",
        duration_months=3,
        vacancies=4,
        deadline=(datetime.utcnow() + timedelta(days=20)).strftime("%Y-%m-%d"),
        is_active=True
    )
    db.session.add(internship4)

    internship5 = Internship(
        company_id=c4_profile.id,
        title="Cybersecurity & Cloud Security Trainee",
        domain="Cybersecurity",
        description="Learn penetration testing, vulnerability analysis, and zero-trust cloud network architecture under seasoned enterprise architects.",
        required_skills="Network Security, Linux, Python, Cryptography, Wireshark, OWASP Top 10, Ethical Hacking",
        responsibilities="1. Perform automated vulnerability scanning.\n2. Review code for security flaws and injection risks.\n3. Document compliance audits and remediation steps.",
        eligibility="Students with coursework in Computer Networks and Information Security.",
        min_cgpa=7.0,
        stipend="₹25,000 / month",
        location="Pune",
        work_mode="On-site",
        duration_months=4,
        vacancies=2,
        deadline=(datetime.utcnow() + timedelta(days=40)).strftime("%Y-%m-%d"),
        is_active=True
    )
    db.session.add(internship5)
    db.session.flush()

    # 4. STUDENT USERS & DYNAMIC RESUMES
    # Student 1: Aarav (Primary Demo Student)
    s1_user = User(email='aarav@email.com', role='student')
    s1_user.set_password('student123')
    db.session.add(s1_user)
    db.session.flush()

    s1_profile = StudentProfile(
        user_id=s1_user.id,
        full_name="Aarav",
        phone="+91 9123456780",
        college_name="National Institute of Technology (NIT)",
        department="Computer Science & Engineering",
        year_of_study="3rd Year (6th Semester)",
        cgpa=8.85,
        bio="Passionate Full Stack Developer and Machine Learning enthusiast with hands-on experience building scalable web applications and intelligent data recommendation systems. Eager to solve real-world industry challenges.",
        location="Bengaluru, Karnataka",
        career_interests="Full Stack Engineering, Machine Learning, Cloud Architecture",
        technical_skills="Python, Flask, React, JavaScript, SQL, Scikit-Learn, Machine Learning, TF-IDF, Git, REST APIs, HTML/CSS, Docker",
        soft_skills="Problem Solving, Team Leadership, Technical Writing, Agile Collaboration",
        github_url="https://github.com/aaravpatel-demo",
        linkedin_url="https://linkedin.com/in/aaravpatel-demo",
        portfolio_url="https://aaravpatel.dev",
        avatar="default-avatar.png"
    )
    db.session.add(s1_profile)
    db.session.flush()

    # S1 Education
    db.session.add(Education(
        student_id=s1_profile.id,
        degree="B.Tech in Computer Science and Engineering",
        institution="National Institute of Technology (NIT)",
        field_of_study="Computer Science",
        start_year="2023",
        end_year="2027",
        grade_or_cgpa="8.85 / 10.0"
    ))
    db.session.add(Education(
        student_id=s1_profile.id,
        degree="Higher Secondary Certificate (Class XII)",
        institution="Delhi Public School",
        field_of_study="Science (PCM + CS)",
        start_year="2021",
        end_year="2023",
        grade_or_cgpa="95.4%"
    ))

    # S1 Experience (Completed previous internship)
    db.session.add(Experience(
        student_id=s1_profile.id,
        title="Summer Software Engineering Intern",
        company_name="Swiggy Engineering",
        location="Bengaluru",
        start_date="May 2025",
        end_date="July 2025",
        is_current=False,
        description="Engineered REST API endpoints in Python Flask for restaurant menu parsing and reduced query response times by 35% through PostgreSQL index optimizations."
    ))

    # S1 Projects
    db.session.add(Project(
        student_id=s1_profile.id,
        title="AI Career & Internship Recommendation Engine",
        technologies="Python, Flask, Scikit-Learn, TF-IDF, Cosine Similarity, React",
        project_url="https://github.com/aaravpatel-demo/internhub-ai",
        description="Designed and deployed an intelligent matching algorithm comparing student resume vector embeddings with job specs using TF-IDF and Random Forest shortlist scoring."
    ))
    db.session.add(Project(
        student_id=s1_profile.id,
        title="E-Commerce Microservices Platform",
        technologies="Python, Docker, Redis, PostgreSQL, React.js",
        project_url="https://github.com/aaravpatel-demo/ecommerce-microservices",
        description="Architected containerized microservices handling authentication, product catalog, payment webhooks, and asynchronous order processing."
    ))

    # S1 Certifications
    db.session.add(Certification(
        student_id=s1_profile.id,
        title="Machine Learning Specialization",
        issuing_organization="DeepLearning.AI / Coursera",
        issue_date="Nov 2025",
        credential_url="https://coursera.org/verify/ML-SPECIALIZATION-RAHUL"
    ))
    db.session.add(Certification(
        student_id=s1_profile.id,
        title="AWS Certified Cloud Practitioner",
        issuing_organization="Amazon Web Services",
        issue_date="Jan 2026",
        credential_url="https://aws.amazon.com/verification/AWS-CP-RAHUL"
    ))

    # Student 2: Priya (Data Science Focus)
    s2_user = User(email='priya@email.com', role='student')
    s2_user.set_password('student123')
    db.session.add(s2_user)
    db.session.flush()

    s2_profile = StudentProfile(
        user_id=s2_user.id,
        full_name="Priya",
        phone="+91 9887766554",
        college_name="IIT Madras",
        department="Data Science & Artificial Intelligence",
        year_of_study="Final Year",
        cgpa=9.3,
        bio="Aspiring AI Research Engineer specializing in Natural Language Processing, Deep Learning, and Computer Vision.",
        location="Chennai, Tamil Nadu",
        career_interests="AI Research, NLP, Deep Learning",
        technical_skills="Python, PyTorch, Deep Learning, Machine Learning, NLP, Scikit-Learn, TensorFlow, SQL, Data Visualization",
        soft_skills="Critical Thinking, Research, Presentation, Collaboration",
        github_url="https://github.com/priyapatel-ai",
        linkedin_url="https://linkedin.com/in/priyapatel-ai"
    )
    db.session.add(s2_profile)
    db.session.flush()

    db.session.add(Education(
        student_id=s2_profile.id,
        degree="B.Tech in Data Science",
        institution="IIT Madras",
        field_of_study="Data Science",
        start_year="2022",
        end_year="2026",
        grade_or_cgpa="9.3 / 10.0"
    ))
    db.session.add(Project(
        student_id=s2_profile.id,
        title="Transformer-Based Clinical Document Summarizer",
        technologies="Python, PyTorch, HuggingFace, BERT, NLP",
        description="Trained domain-adapted BERT model to automatically generate concise summaries of clinical reports with 92% ROUGE-1 score."
    ))

    # Student 3: Rohit (Web Dev Focus)
    s3_user = User(email='rohit@email.com', role='student')
    s3_user.set_password('student123')
    db.session.add(s3_user)
    db.session.flush()

    s3_profile = StudentProfile(
        user_id=s3_user.id,
        full_name="Rohit",
        phone="+91 9776655443",
        college_name="Delhi Technological University (DTU)",
        department="Information Technology",
        year_of_study="3rd Year",
        cgpa=7.9,
        bio="Frontend & UI/UX Developer keen on building accessible, responsive, interactive user experiences.",
        location="New Delhi",
        career_interests="Frontend Engineering, UI/UX Design, Web Applications",
        technical_skills="JavaScript, React, HTML5, CSS3, Tailwind CSS, TypeScript, Figma, Git",
        soft_skills="Creativity, Communication, Team Player",
        github_url="https://github.com/rohitverma-web"
    )
    db.session.add(s3_profile)
    db.session.flush()

    # 5. APPLICATIONS WITH AI SCORES & VARIOUS STATUSES
    # Rahul has a 'Completed' application at Swiggy (internship3) -> Allows him to post a verified review!
    pred_s1_i3 = shortlist_predictor.predict_shortlist_probability(s1_profile, internship3)
    app1 = Application(
        internship_id=internship3.id,
        student_id=s1_profile.id,
        status="Completed",
        tfidf_score=pred_s1_i3['tfidf_score'],
        rf_probability=pred_s1_i3['rf_probability'],
        cover_letter="I have extensive experience in Python backend development, Flask, and database indexing. I am excited to bring these skills to Swiggy.",
        company_notes="Successfully completed 6-month internship with outstanding ratings from team lead.",
        applied_at=datetime.utcnow() - timedelta(days=90),
        updated_at=datetime.utcnow() - timedelta(days=5)
    )
    db.session.add(app1)

    # Rahul applied for Google AI (internship1) -> Shortlisted
    pred_s1_i1 = shortlist_predictor.predict_shortlist_probability(s1_profile, internship1)
    app2 = Application(
        internship_id=internship1.id,
        student_id=s1_profile.id,
        status="Shortlisted",
        tfidf_score=pred_s1_i1['tfidf_score'],
        rf_probability=pred_s1_i1['rf_probability'],
        cover_letter="My projects in TF-IDF recommendation systems and ML algorithms make me a strong candidate for Google's AI Research team.",
        company_notes="High AI match score and strong CGPA. Schedule round 1 interview.",
        applied_at=datetime.utcnow() - timedelta(days=10),
        updated_at=datetime.utcnow() - timedelta(days=2)
    )
    db.session.add(app2)

    # Rahul applied for Microsoft (internship2) -> Under Review
    pred_s1_i2 = shortlist_predictor.predict_shortlist_probability(s1_profile, internship2)
    app3 = Application(
        internship_id=internship2.id,
        student_id=s1_profile.id,
        status="Under Review",
        tfidf_score=pred_s1_i2['tfidf_score'],
        rf_probability=pred_s1_i2['rf_probability'],
        cover_letter="Eager to contribute to Azure developer tools and cloud infrastructure.",
        applied_at=datetime.utcnow() - timedelta(days=3)
    )
    db.session.add(app3)

    # Priya applied for Google AI (internship1) -> Selected
    pred_s2_i1 = shortlist_predictor.predict_shortlist_probability(s2_profile, internship1)
    app4 = Application(
        internship_id=internship1.id,
        student_id=s2_profile.id,
        status="Selected",
        tfidf_score=pred_s2_i1['tfidf_score'],
        rf_probability=pred_s2_i1['rf_probability'],
        cover_letter="My research focus in NLP and deep learning aligns perfectly with Google's research initiatives.",
        company_notes="Exceptional profile and technical interview performance.",
        applied_at=datetime.utcnow() - timedelta(days=15),
        updated_at=datetime.utcnow() - timedelta(days=1)
    )
    db.session.add(app4)

    # Rohit applied for Microsoft (internship2) -> Applied
    pred_s3_i2 = shortlist_predictor.predict_shortlist_probability(s3_profile, internship2)
    app5 = Application(
        internship_id=internship2.id,
        student_id=s3_profile.id,
        status="Applied",
        tfidf_score=pred_s3_i2['tfidf_score'],
        rf_probability=pred_s3_i2['rf_probability'],
        cover_letter="Skilled in React and modern UI development.",
        applied_at=datetime.utcnow() - timedelta(days=1)
    )
    db.session.add(app5)
    db.session.flush()

    # 6. REVIEWS (Sample verified reviews)
    rev1 = Review(
        company_id=c3_profile.id,
        student_id=s1_profile.id,
        internship_id=internship3.id,
        rating=5,
        work_environment_rating=5,
        learning_rating=5,
        mentor_support_rating=5,
        title="Incredible mentorship and massive scale engineering!",
        review_text="My 6-month internship at Swiggy was an eye-opening journey. I got the chance to work directly on high-concurrency order systems, receive code reviews from principal architects, and optimize live production databases. The work culture is super supportive.",
        pros="Great learning curve, supportive mentors, flexible remote options, high stipend.",
        cons="Can get fast-paced during festival demand peaks, but very rewarding."
    )
    db.session.add(rev1)

    # 7. NOTIFICATIONS
    notif1 = Notification(
        user_id=s1_user.id,
        title="Application Shortlisted! 🎉",
        message="Congratulations! Google India Tech has shortlisted your application for AI & Machine Learning Research Intern.",
        category="success",
        link="/student/applications",
        is_read=False
    )
    notif2 = Notification(
        user_id=s1_user.id,
        title="New Matching Internship Alert 🤖",
        message="A new internship 'Full Stack Software Engineer Intern' at Microsoft IDC has an 85% skill match with your dynamic resume!",
        category="info",
        link="/internships",
        is_read=False
    )
    notif3 = Notification(
        user_id=s1_user.id,
        title="Internship Completed ✨",
        message="Your internship at Swiggy Engineering is marked as Completed. You are now verified to write an official company review.",
        category="status",
        link="/student/applications",
        is_read=True
    )
    db.session.add_all([notif1, notif2, notif3])

    # Company notification
    notif_c1 = Notification(
        user_id=c1_user.id,
        title="New High-Match Applicant 🎯",
        message="Aarav (NIT, CGPA 8.85) applied for AI & Machine Learning Research Intern with 88% Match score.",
        category="info",
        link="/company/applicants",
        is_read=False
    )
    db.session.add(notif_c1)

    db.session.commit()
    print("Database seeding completed successfully!")
