import os
import uuid
from datetime import datetime, timedelta
from db_mongo import (
    users_col, students_col, companies_col, internships_col,
    applications_col, reviews_col, notifications_col, MongoHelper
)
from ml_engine import shortlist_predictor

# 10 Diverse Indian tech students with single names (NO surnames in name or email, all @email.com)
STUDENTS_DATA = [
    {
        'email': 'aarav@email.com',
        'full_name': 'Aarav',
        'phone': '+91 9123456780',
        'college_name': 'National Institute of Technology (NIT)',
        'department': 'Computer Science & Engineering',
        'year_of_study': '3rd Year (6th Semester)',
        'cgpa': 8.85,
        'bio': 'Passionate Full Stack Developer and Machine Learning enthusiast with hands-on experience building scalable web applications and intelligent data recommendation systems. Eager to solve real-world industry challenges.',
        'location': 'Bengaluru, Karnataka',
        'career_interests': 'Full Stack Engineering, Machine Learning, Cloud Architecture',
        'technical_skills': 'Python, Flask, React, JavaScript, SQL, Machine Learning, Git, REST APIs, HTML/CSS, Docker',
        'soft_skills': 'Problem Solving, Team Leadership, Technical Writing, Agile Collaboration',
        'github_url': 'https://github.com/aarav-demo',
        'linkedin_url': 'https://linkedin.com/in/aarav-demo',
        'portfolio_url': 'https://aarav.dev',
        'educations': [
            {
                'id': '1',
                'degree': 'B.Tech in Computer Science and Engineering',
                'institution': 'National Institute of Technology (NIT)',
                'field_of_study': 'Computer Science',
                'start_year': '2023',
                'end_year': '2027',
                'grade_or_cgpa': '8.85 / 10.0'
            }
        ],
        'experiences': [
            {
                'id': '1',
                'title': 'Summer Software Engineering Intern',
                'company_name': 'Swiggy Engineering',
                'location': 'Bengaluru',
                'start_date': 'May 2025',
                'end_date': 'July 2025',
                'is_current': False,
                'description': 'Engineered REST API endpoints in Python Flask for restaurant menu parsing and reduced query response times by 35% through database index optimizations.'
            }
        ],
        'projects': [
            {
                'id': '1',
                'title': 'AI Career & Internship Recommendation Engine',
                'technologies': 'Python, Flask, Machine Learning, Data Analytics, React',
                'project_url': 'https://github.com/aarav-demo/internhub-ai',
                'description': 'Designed and deployed an intelligent matching algorithm comparing student resume vector embeddings with job specs using candidate matchmaking and ranking algorithms.'
            },
            {
                'id': '2',
                'title': 'E-Commerce Microservices Platform',
                'technologies': 'Python, Docker, Redis, MongoDB, React.js',
                'project_url': 'https://github.com/aarav-demo/ecommerce-microservices',
                'description': 'Architected containerized microservices handling authentication, product catalog, payment webhooks, and asynchronous order processing.'
            }
        ],
        'certifications': [
            {
                'id': '1',
                'title': 'Machine Learning Specialization',
                'issuing_organization': 'DeepLearning.AI / Coursera',
                'issue_date': 'Nov 2025',
                'credential_url': 'https://coursera.org/verify/ML-SPECIALIZATION-AARAV'
            },
            {
                'id': '2',
                'title': 'AWS Certified Cloud Practitioner',
                'issuing_organization': 'Amazon Web Services',
                'issue_date': 'Jan 2026',
                'credential_url': 'https://aws.amazon.com/verification/AWS-CP-AARAV'
            }
        ]
    },
    {
        'email': 'priya@email.com',
        'full_name': 'Priya',
        'phone': '+91 9845123456',
        'college_name': 'Birla Institute of Technology and Science (BITS Pilani)',
        'department': 'Data Science & Artificial Intelligence',
        'year_of_study': '4th Year (8th Semester)',
        'cgpa': 9.25,
        'bio': 'AI researcher and PyTorch specialist passionate about deep learning, natural language processing, and high-performance neural model inference.',
        'location': 'Bengaluru, Karnataka',
        'career_interests': 'AI Research, Deep Learning, Natural Language Processing',
        'technical_skills': 'Python, PyTorch, TensorFlow, Deep Learning, NLP, Scikit-Learn, Pandas, NumPy, Computer Vision, Docker, Data Structures',
        'soft_skills': 'Research Methodologies, Analytical Thinking, Scientific Paper Writing',
        'github_url': 'https://github.com/priya-ai',
        'linkedin_url': 'https://linkedin.com/in/priya-ai',
        'portfolio_url': 'https://priya.tech',
        'educations': [
            {
                'id': '1',
                'degree': 'B.Tech in Artificial Intelligence & Data Science',
                'institution': 'BITS Pilani',
                'field_of_study': 'AI & Robotics',
                'start_year': '2022',
                'end_year': '2026',
                'grade_or_cgpa': '9.25 / 10.0'
            }
        ],
        'experiences': [
            {
                'id': '1',
                'title': 'Computer Vision Research Fellow',
                'company_name': 'IISc Research Labs',
                'location': 'Bengaluru',
                'start_date': 'Jan 2025',
                'end_date': 'June 2025',
                'is_current': False,
                'description': 'Trained transformer models for biomedical image segmentation, achieving 94.2% Dice coefficient.'
            }
        ],
        'projects': [
            {
                'id': '1',
                'title': 'Multilingual Medical NLP Summarizer',
                'technologies': 'Python, PyTorch, HuggingFace, FastAPI, React',
                'project_url': 'https://github.com/priya-ai/med-summarizer',
                'description': 'Built an abstractive clinical record summarization pipeline using fine-tuned transformer architectures.'
            }
        ],
        'certifications': [
            {
                'id': '1',
                'title': 'Deep Learning Specialization',
                'issuing_organization': 'DeepLearning.AI',
                'issue_date': 'Dec 2024',
                'credential_url': 'https://coursera.org/verify/DL-PRIYA'
            }
        ]
    },
    {
        'email': 'rohit@email.com',
        'full_name': 'Rohit',
        'phone': '+91 9711223344',
        'college_name': 'IIIT Hyderabad',
        'department': 'Computer Science & Engineering',
        'year_of_study': '3rd Year (6th Semester)',
        'cgpa': 8.40,
        'bio': 'High-performance backend architect focusing on distributed storage, asynchronous messaging, and scalable microservices with Python and Go.',
        'location': 'Hyderabad, Telangana',
        'career_interests': 'Backend Systems, Distributed Databases, Cloud Infrastructure',
        'technical_skills': 'Python, Flask, Django, PostgreSQL, Redis, Microservices, System Design, Algorithms, Docker, Linux, SQL',
        'soft_skills': 'Systems Thinking, Code Review, Fast Troubleshooting',
        'github_url': 'https://github.com/rohit-code',
        'linkedin_url': 'https://linkedin.com/in/rohit-code',
        'portfolio_url': 'https://rohit.dev',
        'educations': [
            {
                'id': '1',
                'degree': 'B.Tech in Computer Science',
                'institution': 'IIIT Hyderabad',
                'field_of_study': 'Computer Systems',
                'start_year': '2023',
                'end_year': '2027',
                'grade_or_cgpa': '8.40 / 10.0'
            }
        ],
        'experiences': [
            {
                'id': '1',
                'title': 'Backend Developer Intern',
                'company_name': 'Razorpay',
                'location': 'Bengaluru',
                'start_date': 'June 2025',
                'end_date': 'August 2025',
                'is_current': False,
                'description': 'Developed idempotent webhook handling services processing over 50,000 requests per minute with Redis caching.'
            }
        ],
        'projects': [
            {
                'id': '1',
                'title': 'Distributed Key-Value Store in Python',
                'technologies': 'Python, Raft Consensus, gRPC, Socket Programming',
                'project_url': 'https://github.com/rohit-code/distributed-kv',
                'description': 'Implemented Raft consensus algorithm for fault-tolerant state machine replication across cluster nodes.'
            }
        ],
        'certifications': [
            {
                'id': '1',
                'title': 'Certified Kubernetes Administrator (CKA)',
                'issuing_organization': 'Linux Foundation',
                'issue_date': 'Jan 2026',
                'credential_url': 'https://lf.org/verify/CKA-ROHIT'
            }
        ]
    },
    {
        'email': 'ananya@email.com',
        'full_name': 'Ananya',
        'phone': '+91 9940112233',
        'college_name': 'College of Engineering Guindy (Anna University)',
        'department': 'Information Technology',
        'year_of_study': '4th Year (7th Semester)',
        'cgpa': 8.95,
        'bio': 'Frontend developer and TypeScript enthusiast creating delightful, accessible, and high-speed web experiences with React and Next.js.',
        'location': 'Chennai, Tamil Nadu',
        'career_interests': 'Frontend Development, UI/UX Systems, Cloud Web Applications',
        'technical_skills': 'React, TypeScript, Node.js, Next.js, REST APIs, SQL, Docker, Git, Cloud Computing, HTML/CSS, Tailwind CSS',
        'soft_skills': 'Design Sensitivity, Cross-functional Communication, Empathy',
        'github_url': 'https://github.com/ananya-ui',
        'linkedin_url': 'https://linkedin.com/in/ananya-ui',
        'portfolio_url': 'https://ananya.com',
        'educations': [
            {
                'id': '1',
                'degree': 'B.Tech in Information Technology',
                'institution': 'CEG Anna University',
                'field_of_study': 'Web Systems & Human-Computer Interaction',
                'start_year': '2022',
                'end_year': '2026',
                'grade_or_cgpa': '8.95 / 10.0'
            }
        ],
        'experiences': [
            {
                'id': '1',
                'title': 'Frontend Engineering Intern',
                'company_name': 'Freshworks',
                'location': 'Chennai',
                'start_date': 'May 2025',
                'end_date': 'July 2025',
                'is_current': False,
                'description': 'Revamped the customer onboarding flow with React 19 and custom design tokens, lifting completion conversion by 28%.'
            }
        ],
        'projects': [
            {
                'id': '1',
                'title': 'Collaborative Real-time Canvas',
                'technologies': 'React, TypeScript, WebSockets, WebGL, Tailwind',
                'project_url': 'https://github.com/ananya-ui/realtime-canvas',
                'description': 'Built an interactive collaborative whiteboard featuring 60fps latency-free stroke synchronization.'
            }
        ],
        'certifications': [
            {
                'id': '1',
                'title': 'Meta Front-End Developer Professional Certificate',
                'issuing_organization': 'Meta / Coursera',
                'issue_date': 'Aug 2025',
                'credential_url': 'https://coursera.org/verify/META-ANANYA'
            }
        ]
    },
    {
        'email': 'karthik@email.com',
        'full_name': 'Karthik',
        'phone': '+91 9443123456',
        'college_name': 'PSG College of Technology, Coimbatore',
        'department': 'Software Systems',
        'year_of_study': '3rd Year (5th Semester)',
        'cgpa': 7.90,
        'bio': 'Practical software engineer with solid foundations in Java, Python, and relational database schema design. Motivated to learn agile cloud engineering.',
        'location': 'Coimbatore, Tamil Nadu',
        'career_interests': 'Enterprise Software, Database Optimization, Microservices',
        'technical_skills': 'Python, Java, Spring Boot, MySQL, REST APIs, Git, Docker, HTML/CSS, Linux, SQL',
        'soft_skills': 'Persistence, Active Listening, Team Player',
        'github_url': 'https://github.com/karthik-dev',
        'linkedin_url': 'https://linkedin.com/in/karthik-dev',
        'portfolio_url': 'https://karthik.me',
        'educations': [
            {
                'id': '1',
                'degree': 'M.Sc. Integrated Software Systems',
                'institution': 'PSG College of Technology',
                'field_of_study': 'Software Engineering',
                'start_year': '2023',
                'end_year': '2028',
                'grade_or_cgpa': '7.90 / 10.0'
            }
        ],
        'experiences': [],
        'projects': [
            {
                'id': '1',
                'title': 'Campus Placement Automation Portal',
                'technologies': 'Python, Flask, MySQL, Bootstrap',
                'project_url': 'https://github.com/karthik-dev/placement-portal',
                'description': 'Developed an end-to-end recruitment tracker for college campus placement drives managing 1,200+ students.'
            }
        ],
        'certifications': [
            {
                'id': '1',
                'title': 'Oracle Certified Associate, Java SE 8 Programmer',
                'issuing_organization': 'Oracle',
                'issue_date': 'May 2025',
                'credential_url': 'https://oracle.com/verify/OCA-KARTHIK'
            }
        ]
    },
    {
        'email': 'sneha@email.com',
        'full_name': 'Sneha',
        'phone': '+91 9822334455',
        'college_name': 'College of Engineering Pune (COEP)',
        'department': 'Computer Engineering',
        'year_of_study': '4th Year (8th Semester)',
        'cgpa': 9.15,
        'bio': 'Data science practitioner interested in statistical modeling, predictive analytics, and building enterprise dashboards that translate numbers into business impact.',
        'location': 'Pune, Maharashtra',
        'career_interests': 'Data Science, Machine Learning, Business Intelligence',
        'technical_skills': 'Python, Machine Learning, Scikit-Learn, PowerBI, Tableau, SQL, Statistics, Pandas, NumPy, Deep Learning Basics',
        'soft_skills': 'Data Storytelling, Stakeholder Communication, Critical Thinking',
        'github_url': 'https://github.com/sneha-ds',
        'linkedin_url': 'https://linkedin.com/in/sneha-ds',
        'portfolio_url': 'https://sneha.info',
        'educations': [
            {
                'id': '1',
                'degree': 'B.Tech in Computer Engineering',
                'institution': 'COEP Pune',
                'field_of_study': 'Computer Science & Mathematics',
                'start_year': '2022',
                'end_year': '2026',
                'grade_or_cgpa': '9.15 / 10.0'
            }
        ],
        'experiences': [
            {
                'id': '1',
                'title': 'Data Science Intern',
                'company_name': 'Tata Consultancy Services',
                'location': 'Pune',
                'start_date': 'Dec 2024',
                'end_date': 'Feb 2025',
                'is_current': False,
                'description': 'Built customer churn prediction models using Random Forest and XGBoost with an AUC of 0.89.'
            }
        ],
        'projects': [
            {
                'id': '1',
                'title': 'Predictive Health Risk Assessment Model',
                'technologies': 'Python, Scikit-Learn, Streamlit, Pandas, Seaborn',
                'project_url': 'https://github.com/sneha-ds/health-risk-ml',
                'description': 'Trained classification pipelines on public health cohorts to predict cardiovascular onset factors.'
            }
        ],
        'certifications': [
            {
                'id': '1',
                'title': 'IBM Data Science Professional Certificate',
                'issuing_organization': 'IBM',
                'issue_date': 'Sep 2024',
                'credential_url': 'https://coursera.org/verify/IBM-SNEHA'
            }
        ]
    },
    {
        'email': 'aditya@email.com',
        'full_name': 'Aditya',
        'phone': '+91 9895112233',
        'college_name': 'National Institute of Technology Calicut (NITC)',
        'department': 'Electronics & Communication Engineering',
        'year_of_study': '3rd Year (6th Semester)',
        'cgpa': 8.10,
        'bio': 'Systems programmer working at the intersection of embedded hardware, C++, and edge computer vision. Excited about robotics and AI automation.',
        'location': 'Kozhikode, Kerala',
        'career_interests': 'Edge Computing, Robotics, Embedded Systems, Machine Learning',
        'technical_skills': 'C++, Python, Embedded Systems, Linux, Git, Algorithms, Data Structures, OpenCV, Machine Learning Basics',
        'soft_skills': 'Hands-on Prototyping, Technical Curiosity, Reliability',
        'github_url': 'https://github.com/aditya-embed',
        'linkedin_url': 'https://linkedin.com/in/aditya-embed',
        'portfolio_url': 'https://aditya.dev',
        'educations': [
            {
                'id': '1',
                'degree': 'B.Tech in Electronics & Communication',
                'institution': 'NIT Calicut',
                'field_of_study': 'Signal Processing & Embedded Microcontrollers',
                'start_year': '2023',
                'end_year': '2027',
                'grade_or_cgpa': '8.10 / 10.0'
            }
        ],
        'experiences': [],
        'projects': [
            {
                'id': '1',
                'title': 'Autonomous Line & Obstacle Navigating Bot',
                'technologies': 'C++, ROS2, OpenCV, Raspberry Pi, Python',
                'project_url': 'https://github.com/aditya-embed/autonomous-bot',
                'description': 'Built an autonomous obstacle-avoiding mobile robot utilizing ROS2 nodes and camera-based edge inference.'
            }
        ],
        'certifications': [
            {
                'id': '1',
                'title': 'Introduction to Self-Driving Cars',
                'issuing_organization': 'University of Toronto',
                'issue_date': 'Nov 2025',
                'credential_url': 'https://coursera.org/verify/AUTONOMOUS-ADITYA'
            }
        ]
    },
    {
        'email': 'pooja@email.com',
        'full_name': 'Pooja',
        'phone': '+91 9988776655',
        'college_name': 'Osmania University College of Engineering',
        'department': 'Artificial Intelligence & Machine Learning',
        'year_of_study': '2nd Year (4th Semester)',
        'cgpa': 8.65,
        'bio': 'Aspiring AI software engineer with a strong focus on data manipulation, REST APIs, and clean data visualization.',
        'location': 'Hyderabad, Telangana',
        'career_interests': 'AI Engineering, Full Stack Web Development, Cloud Computing',
        'technical_skills': 'Python, Data Analytics, Flask, SQL, HTML/CSS, JavaScript, Seaborn, Matplotlib, Git, REST APIs',
        'soft_skills': 'Fast Learner, Collaborative Mindset, Creative Problem Solving',
        'github_url': 'https://github.com/pooja-ai',
        'linkedin_url': 'https://linkedin.com/in/pooja-ai',
        'portfolio_url': 'https://pooja.me',
        'educations': [
            {
                'id': '1',
                'degree': 'B.E. in Artificial Intelligence & Machine Learning',
                'institution': 'Osmania University',
                'field_of_study': 'Artificial Intelligence',
                'start_year': '2024',
                'end_year': '2028',
                'grade_or_cgpa': '8.65 / 10.0'
            }
        ],
        'experiences': [],
        'projects': [
            {
                'id': '1',
                'title': 'Smart Expense Tracker with Analytics',
                'technologies': 'Python, Flask, SQLite, Chart.js',
                'project_url': 'https://github.com/pooja-ai/smart-expenses',
                'description': 'Created a dynamic budget analyzer featuring automatic recurring expense categorizations and interactive monthly spending trends.'
            }
        ],
        'certifications': [
            {
                'id': '1',
                'title': 'Python for Everybody Specialization',
                'issuing_organization': 'University of Michigan',
                'issue_date': 'Oct 2024',
                'credential_url': 'https://coursera.org/verify/PY-POOJA'
            }
        ]
    },
    {
        'email': 'vikram@email.com',
        'full_name': 'Vikram',
        'phone': '+91 9811223344',
        'college_name': 'Delhi Technological University (DTU)',
        'department': 'Software Engineering',
        'year_of_study': '4th Year (7th Semester)',
        'cgpa': 8.50,
        'bio': 'Cloud and DevOps engineer focused on automated CI/CD pipelines, container orchestration, and multi-cloud infrastructure deployment.',
        'location': 'New Delhi, Delhi NCR',
        'career_interests': 'DevOps, Cloud Computing, Site Reliability Engineering',
        'technical_skills': 'Python, Docker, Kubernetes, Cloud Computing, Microservices, Linux, CI/CD, Terraform, SQL, Git, REST APIs',
        'soft_skills': 'Incident Management, System Resilience, Team Mentorship',
        'github_url': 'https://github.com/vikram-cloud',
        'linkedin_url': 'https://linkedin.com/in/vikram-cloud',
        'portfolio_url': 'https://vikram.cloud',
        'educations': [
            {
                'id': '1',
                'degree': 'B.Tech in Software Engineering',
                'institution': 'Delhi Technological University (DTU)',
                'field_of_study': 'Cloud Systems & Infrastructure',
                'start_year': '2022',
                'end_year': '2026',
                'grade_or_cgpa': '8.50 / 10.0'
            }
        ],
        'experiences': [
            {
                'id': '1',
                'title': 'Cloud Engineering Intern',
                'company_name': 'Zomato Infrastructure Team',
                'location': 'Gurugram',
                'start_date': 'May 2025',
                'end_date': 'July 2025',
                'is_current': False,
                'description': 'Automated container build manifests and saved 22% in monthly AWS staging cluster resource utilization.'
            }
        ],
        'projects': [
            {
                'id': '1',
                'title': 'Multi-Environment GitOps Deployment Operator',
                'technologies': 'Kubernetes, Go, Python, Docker, GitHub Actions',
                'project_url': 'https://github.com/vikram-cloud/gitops-operator',
                'description': 'Architected a lightweight Kubernetes operator for continuous cluster configuration synchronization.'
            }
        ],
        'certifications': [
            {
                'id': '1',
                'title': 'AWS Certified Solutions Architect – Associate',
                'issuing_organization': 'Amazon Web Services',
                'issue_date': 'Aug 2025',
                'credential_url': 'https://aws.amazon.com/verification/AWS-SA-VIKRAM'
            }
        ]
    },
    {
        'email': 'meera@email.com',
        'full_name': 'Meera',
        'phone': '+91 9820123456',
        'college_name': 'Veermata Jijabai Technological Institute (VJTI Mumbai)',
        'department': 'Computer Engineering',
        'year_of_study': '3rd Year (6th Semester)',
        'cgpa': 8.75,
        'bio': 'Mobile app and full stack developer specializing in cross-platform experiences using React, Flutter, and REST backend services.',
        'location': 'Mumbai, Maharashtra',
        'career_interests': 'Mobile Engineering, Full Stack Web, Interactive Interfaces',
        'technical_skills': 'React, JavaScript, Python, REST APIs, Git, HTML/CSS, SQL, Docker, Mobile Development Basics',
        'soft_skills': 'User-Centered Thinking, Visual Design, Adaptability',
        'github_url': 'https://github.com/meera-app',
        'linkedin_url': 'https://linkedin.com/in/meera-app',
        'portfolio_url': 'https://meera.design',
        'educations': [
            {
                'id': '1',
                'degree': 'B.Tech in Computer Engineering',
                'institution': 'VJTI Mumbai',
                'field_of_study': 'Computer Science & Human Interaction',
                'start_year': '2023',
                'end_year': '2027',
                'grade_or_cgpa': '8.75 / 10.0'
            }
        ],
        'experiences': [],
        'projects': [
            {
                'id': '1',
                'title': 'Student Mental Wellness & Habit Mobile Tracker',
                'technologies': 'React Native, Node.js, Express, MongoDB',
                'project_url': 'https://github.com/meera-app/wellness-tracker',
                'description': 'Designed and released a clean cross-platform wellness application with 1,500+ active student users.'
            }
        ],
        'certifications': [
            {
                'id': '1',
                'title': 'Full Stack Web Development with React Specialization',
                'issuing_organization': 'The Hong Kong University of Science and Technology',
                'issue_date': 'Jan 2025',
                'credential_url': 'https://coursera.org/verify/REACT-MEERA'
            }
        ]
    }
]

# Single Primary Platform Administrator
ADMIN_EMAIL = 'admin@internhub.com'
ADMIN_PASSWORD = 'admin123'


def seed_mongo():
    # 0. Sanitize existing student records: remove all surnames from email & full_name, and migrate student domains to @email.com
    try:
        # Convert any existing student emails to @email.com and strip surnames
        for u in list(users_col.find({'role': 'student'})):
            old_email = u.get('email', '')
            if '@' in old_email:
                prefix = old_email.split('@')[0]
                if '.' in prefix:
                    prefix = prefix.split('.')[0]
                new_email = f"{prefix}@email.com"
                if old_email != new_email:
                    collision = users_col.find_one({'email': new_email, '_id': {'$ne': u['_id']}})
                    if collision:
                        users_col.delete_one({'_id': u['_id']})
                    else:
                        users_col.update_one({'_id': u['_id']}, {'$set': {'email': new_email}})

        # Remove any student users lingering on @internhub.com domain
        users_col.delete_many({'role': 'student', 'email': {'$regex': r'@internhub\.com$'}})

        # Update full_name to single first name (remove any surnames)
        for s in list(students_col.find()):
            name = s.get('full_name', '').strip()
            if ' ' in name:
                first_name_only = name.split()[0]
                students_col.update_one({'_id': s['_id']}, {'$set': {'full_name': first_name_only}})
    except Exception as e:
        print(f"Student sanitization note: {e}")

    # 1. Seed or Verify all 10 Companies and their respective internships
    _seed_companies_and_internships()

    # 2. Ensure the single Admin exists
    existing_admin = users_col.find_one({'email': ADMIN_EMAIL})
    if not existing_admin:
        MongoHelper.create_user(ADMIN_EMAIL, ADMIN_PASSWORD, 'admin')

    # Remove any extra admins if previously generated (keep only single primary admin)
    users_col.delete_many({'role': 'admin', 'email': {'$ne': ADMIN_EMAIL}})

    # 3. Ensure all 10 Students exist (none with sub-name Sharma)
    c_jobs = list(internships_col.find({'is_active': True}))
    for idx, s_data in enumerate(STUDENTS_DATA):
        existing_user = users_col.find_one({'email': s_data['email']})
        if not existing_user:
            u = MongoHelper.create_user(s_data['email'], 'student123', 'student')
            doc = {
                'user_id': str(u['id']),
                'full_name': s_data['full_name'],
                'phone': s_data['phone'],
                'college_name': s_data['college_name'],
                'department': s_data['department'],
                'year_of_study': s_data['year_of_study'],
                'cgpa': s_data['cgpa'],
                'bio': s_data['bio'],
                'location': s_data['location'],
                'career_interests': s_data['career_interests'],
                'technical_skills': s_data['technical_skills'],
                'soft_skills': s_data['soft_skills'],
                'github_url': s_data['github_url'],
                'linkedin_url': s_data['linkedin_url'],
                'portfolio_url': s_data['portfolio_url'],
                'avatar': 'default-avatar.png',
                'educations': s_data['educations'],
                'experiences': s_data['experiences'],
                'projects': s_data['projects'],
                'certifications': s_data['certifications'],
                'updated_at': datetime.utcnow()
            }
            res = students_col.insert_one(doc)
            s_id = str(res.inserted_id)
            doc['id'] = s_id

            # Create sample application if jobs exist
            if c_jobs:
                target_job = c_jobs[idx % len(c_jobs)]
                pred = shortlist_predictor.predict_shortlist_probability(doc, target_job)
                status = "Shortlisted" if pred['rf_probability'] >= 70 else ("Applied" if pred['rf_probability'] >= 50 else "Under Review")
                applications_col.insert_one({
                    'internship_id': str(target_job['_id']),
                    'student_id': s_id,
                    'status': status,
                    'tfidf_score': pred['tfidf_score'],
                    'rf_probability': pred['rf_probability'],
                    'cover_letter': f"I am deeply excited to apply for {target_job.get('title')}. My background in {s_data['department']} aligns strongly with your technical requirements.",
                    'company_notes': "Automated matching score computed against student profile.",
                    'applied_at': datetime.utcnow() - timedelta(days=(idx * 2) % 14 + 1),
                    'updated_at': datetime.utcnow()
                })

    # Allow logging in with either aarav@email.com or student@email.com (both have zero surnames)
    if not users_col.find_one({'email': 'student@email.com'}):
        u_alias = MongoHelper.create_user('student@email.com', 'student123', 'student')
        aarav_sp = students_col.find_one({'full_name': 'Aarav'})
        if aarav_sp:
            alias_doc = dict(aarav_sp)
            alias_doc.pop('_id', None)
            alias_doc['user_id'] = str(u_alias['id'])
            students_col.insert_one(alias_doc)

    print(f"MongoDB seed verified! Total Admins: {users_col.count_documents({'role': 'admin'})}, Total Companies: {companies_col.count_documents({})}, Total Students: {students_col.count_documents({})}, Total Internships: {internships_col.count_documents({})}")


COMPANIES_DATA = [
    {
        'email': 'hr@google.com',
        'company_name': "Google India Tech",
        'industry': "Software & AI",
        'website': "https://careers.google.com",
        'location': "Bengaluru, Karnataka",
        'description': "Google's mission is to organize the world's information and make it universally accessible and useful. We build products that help billions of users.",
        'contact_person': "Ananya Rao (Tech Talent Lead)",
        'phone': "+91 9876543210",
        'logo': "google-logo.png",
        'internship': {
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
    },
    {
        'email': 'talent@microsoft.com',
        'company_name': "Microsoft IDC",
        'industry': "Cloud & Enterprise Software",
        'website': "https://careers.microsoft.com",
        'location': "Hyderabad, Telangana",
        'description': "Microsoft enables digital transformation for the era of an intelligent cloud and an intelligent edge. Join our Azure and Developer tools teams.",
        'contact_person': "Vikram Malhotra (Campus Recruitment)",
        'phone': "+91 9876543211",
        'logo': "microsoft-logo.png",
        'internship': {
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
    },
    {
        'email': 'careers@swiggy.in',
        'company_name': "Swiggy Engineering",
        'industry': "E-Commerce & Food Tech",
        'website': "https://swiggy.careers",
        'location': "Bengaluru, Karnataka",
        'description': "Swiggy is India's leading on-demand convenience platform. We solve high-scale hyper-local logistics and real-time dispatch systems.",
        'contact_person': "Kavita Reddy (HR Manager)",
        'phone': "+91 9876543212",
        'logo': "swiggy-logo.png",
        'internship': {
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
    },
    {
        'email': 'jobs@amazon.in',
        'company_name': "Amazon Development Centre",
        'industry': "Cloud Computing & E-Commerce",
        'website': "https://amazon.jobs",
        'location': "Hyderabad, Telangana",
        'description': "Amazon is guided by four principles: customer obsession, passion for invention, commitment to operational excellence, and long-term thinking.",
        'contact_person': "Rajesh Nambiar (Talent Acquisition)",
        'phone': "+91 9876543213",
        'logo': "amazon-logo.png",
        'internship': {
            'title': "Cloud Infrastructure & DevOps Intern",
            'domain': "Cloud Computing",
            'description': "Build resilient continuous deployment pipelines and cloud automation tools supporting Amazon AWS infrastructure at worldwide scale.",
            'required_skills': "Python, Docker, Kubernetes, Cloud Computing, Linux, CI/CD, Terraform, AWS, SQL",
            'responsibilities': "1. Automate cloud provisioning with Infrastructure as Code.\n2. Improve observability and latency telemetry.\n3. Implement auto-scaling policies.",
            'eligibility': "Pre-final and Final year B.Tech students in CS/IT with solid Linux and networking knowledge.",
            'min_cgpa': 7.8,
            'stipend': "₹48,000 / month",
            'location': "Hyderabad (Hybrid)",
            'work_mode': "Hybrid",
            'duration_months': 6,
            'vacancies': 4,
            'deadline': (datetime.utcnow() + timedelta(days=28)).strftime("%Y-%m-%d"),
            'is_active': True,
            'created_at': datetime.utcnow()
        }
    },
    {
        'email': 'talent@flipkart.com',
        'company_name': "Flipkart Tech Labs",
        'industry': "E-Commerce & Supply Chain Tech",
        'website': "https://flipkartcareers.com",
        'location': "Bengaluru, Karnataka",
        'description': "Flipkart is India's homegrown e-commerce pioneer, democratizing commerce for 500M+ Indians through data engineering and supply-chain innovation.",
        'contact_person': "Divya Sundaram (University Relations)",
        'phone': "+91 9876543214",
        'logo': "flipkart-logo.png",
        'internship': {
            'title': "Data Engineering & Analytics Intern",
            'domain': "Data Science",
            'description': "Design scalable ETL data pipelines handling petabyte-scale clickstream telemetry and real-time inventory reconciliation.",
            'required_skills': "Python, SQL, Apache Spark, Pandas, Data Analytics, Microservices, Algorithms, Git",
            'responsibilities': "1. Build automated batch and streaming data pipelines.\n2. Optimize columnar data warehouse queries.\n3. Create real-time executive analytics dashboards.",
            'eligibility': "Students strong in SQL, Python data structures, and database principles.",
            'min_cgpa': 7.5,
            'stipend': "₹38,000 / month",
            'location': "Bengaluru",
            'work_mode': "Hybrid",
            'duration_months': 6,
            'vacancies': 3,
            'deadline': (datetime.utcnow() + timedelta(days=20)).strftime("%Y-%m-%d"),
            'is_active': True,
            'created_at': datetime.utcnow()
        }
    },
    {
        'email': 'campus@tcs.com',
        'company_name': "TCS Research & Innovations",
        'industry': "Enterprise Software & AI Research",
        'website': "https://tcs.com/careers",
        'location': "Chennai, Tamil Nadu",
        'description': "Tata Consultancy Services is an IT services, consulting, and business solutions organization that has been partnering with the world's largest businesses.",
        'contact_person': "Balaji Venkatesh (Campus Lead)",
        'phone': "+91 9876543215",
        'logo': "tcs-logo.png",
        'internship': {
            'title': "Applied Computer Vision & NLP Research Trainee",
            'domain': "Artificial Intelligence",
            'description': "Conduct applied research on document intelligence, optical character recognition (OCR), and conversational AI assistants for banking and healthcare.",
            'required_skills': "Python, Machine Learning, OpenCV, PyTorch, Scikit-Learn, NLP, Deep Learning, Statistics",
            'responsibilities': "1. Fine-tune transformer models for semantic document parsing.\n2. Benchmark inference speeds on edge devices.\n3. Present findings to senior scientists.",
            'eligibility': "Engineering students with coursework in Artificial Intelligence, Computer Vision, or NLP.",
            'min_cgpa': 7.5,
            'stipend': "₹30,000 / month",
            'location': "Chennai",
            'work_mode': "On-site",
            'duration_months': 6,
            'vacancies': 5,
            'deadline': (datetime.utcnow() + timedelta(days=35)).strftime("%Y-%m-%d"),
            'is_active': True,
            'created_at': datetime.utcnow()
        }
    },
    {
        'email': 'recruitment@infosys.com',
        'company_name': "Infosys Digital Labs",
        'industry': "Digital Transformation & Cloud Services",
        'website': "https://infosys.com/careers",
        'location': "Bengaluru, Karnataka",
        'description': "Infosys is a global leader in next-generation digital services and consulting, enabling clients across 56 countries to navigate digital transformation.",
        'contact_person': "Snehal Deshmukh (Talent Head)",
        'phone': "+91 9876543216",
        'logo': "infosys-logo.png",
        'internship': {
            'title': "Modern Web & Full Stack Developer Trainee",
            'domain': "Software Development",
            'description': "Build responsive enterprise web portals using React, TypeScript, and micro-frontend architectures with automated testing.",
            'required_skills': "React, JavaScript, TypeScript, HTML/CSS, REST APIs, Git, SQL, Bootstrap, Tailwind CSS",
            'responsibilities': "1. Implement modular UI widgets with modern state management.\n2. Connect frontend views to backend REST endpoints.\n3. Ensure high accessibility (WCAG) and cross-browser consistency.",
            'eligibility': "Students passionate about modern UI development with hands-on JavaScript/React project portfolios.",
            'min_cgpa': 7.0,
            'stipend': "₹32,000 / month",
            'location': "Bengaluru (Hybrid)",
            'work_mode': "Hybrid",
            'duration_months': 3,
            'vacancies': 6,
            'deadline': (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d"),
            'is_active': True,
            'created_at': datetime.utcnow()
        }
    },
    {
        'email': 'hiring@zomato.com',
        'company_name': "Zomato Engineering",
        'industry': "Consumer Tech & Hyperlocal Logistics",
        'website': "https://zomato.com/careers",
        'location': "Gurugram, Delhi NCR",
        'description': "Zomato's mission is better food for more people. We build frictionless consumer ordering, live rider dispatch, and restaurant partner analytics.",
        'contact_person': "Tarun Gupta (Lead Engineering Recruiter)",
        'phone': "+91 9876543217",
        'logo': "zomato-logo.png",
        'internship': {
            'title': "Mobile Application Developer Intern (React Native / Flutter)",
            'domain': "Mobile Development",
            'description': "Join our rider and consumer mobile apps team to create smooth 60fps animations, offline caching, and real-time GPS tracking experiences.",
            'required_skills': "React Native, Flutter, JavaScript, Mobile Development Basics, REST APIs, Git, Firebase, UI/UX Design",
            'responsibilities': "1. Develop performant mobile screens with fluid gestures.\n2. Integrate live WebSocket location pings.\n3. Optimize app startup times and memory footprint.",
            'eligibility': "Developers experienced in cross-platform mobile app development with published GitHub projects.",
            'min_cgpa': 7.2,
            'stipend': "₹36,000 / month",
            'location': "Gurugram / Remote",
            'work_mode': "Remote",
            'duration_months': 3,
            'vacancies': 3,
            'deadline': (datetime.utcnow() + timedelta(days=22)).strftime("%Y-%m-%d"),
            'is_active': True,
            'created_at': datetime.utcnow()
        }
    },
    {
        'email': 'careers@razorpay.com',
        'company_name': "Razorpay Payments",
        'industry': "FinTech & Payment Infrastructure",
        'website': "https://razorpay.com/jobs",
        'location': "Bengaluru, Karnataka",
        'description': "Razorpay powers seamless payment gateways, automated payouts, neo-banking, and corporate credit cards for millions of Indian businesses.",
        'contact_person': "Neha Sengupta (FinTech Talent Partner)",
        'phone': "+91 9876543218",
        'logo': "razorpay-logo.png",
        'internship': {
            'title': "FinTech API & Security Engineering Intern",
            'domain': "Backend Engineering",
            'description': "Architect bank-grade payment checkout APIs, cryptographic signature verifications, and fraud detection microservices.",
            'required_skills': "Python, Go, PostgreSQL, Redis, REST APIs, Microservices, System Design, SQL, Docker",
            'responsibilities': "1. Implement high-reliability webhook delivery engines.\n2. Harden API endpoints with rate limiters and cryptographic tokens.\n3. Conduct load testing for festive flash sales.",
            'eligibility': "Students with deep interest in backend systems, distributed locks, and secure API design.",
            'min_cgpa': 7.8,
            'stipend': "₹42,000 / month",
            'location': "Bengaluru (Hybrid)",
            'work_mode': "Hybrid",
            'duration_months': 6,
            'vacancies': 3,
            'deadline': (datetime.utcnow() + timedelta(days=18)).strftime("%Y-%m-%d"),
            'is_active': True,
            'created_at': datetime.utcnow()
        }
    },
    {
        'email': 'talent@jio.com',
        'company_name': "Jio Platforms",
        'industry': "Telecom, Cloud & 5G Platforms",
        'website': "https://jio.com/careers",
        'location': "Navi Mumbai, Maharashtra",
        'description': "Jio Platforms is transforming India into a premier digital society through 5G network cloudification, fiber broadband, and cutting-edge digital enterprise apps.",
        'contact_person': "Harish Kulkarni (Strategic HR Partner)",
        'phone': "+91 9876543219",
        'logo': "jio-logo.png",
        'internship': {
            'title': "Distributed Systems & 5G Network Automation Intern",
            'domain': "Software Development",
            'description': "Build cloud-native orchestration controllers and automated monitoring daemons for large-scale enterprise 5G networks.",
            'required_skills': "Python, C++, Linux, Docker, Kubernetes, Algorithms, Data Structures, Git, Cloud Computing",
            'responsibilities': "1. Develop automated health check microservices for telecom pods.\n2. Analyze network traffic telemetry and latency anomalies.\n3. Script automated regression verification suites in Python.",
            'eligibility': "Passionate software engineering students with strong computer architecture and systems fundamentals.",
            'min_cgpa': 7.5,
            'stipend': "₹35,000 / month",
            'location': "Navi Mumbai",
            'work_mode': "On-site",
            'duration_months': 6,
            'vacancies': 4,
            'deadline': (datetime.utcnow() + timedelta(days=25)).strftime("%Y-%m-%d"),
            'is_active': True,
            'created_at': datetime.utcnow()
        }
    }
]


def _seed_companies_and_internships():
    for c_info in COMPANIES_DATA:
        c_user = users_col.find_one({'email': c_info['email']})
        if not c_user:
            c_user = MongoHelper.create_user(c_info['email'], 'company123', 'company')
        
        c_profile = companies_col.find_one({'company_name': c_info['company_name']})
        if not c_profile:
            c_doc = {
                'user_id': str(c_user['id']),
                'company_name': c_info['company_name'],
                'industry': c_info['industry'],
                'website': c_info['website'],
                'location': c_info['location'],
                'description': c_info['description'],
                'contact_person': c_info['contact_person'],
                'phone': c_info['phone'],
                'is_verified': True,
                'logo': c_info['logo'],
                'created_at': datetime.utcnow()
            }
            c_id = companies_col.insert_one(c_doc).inserted_id
        else:
            c_id = c_profile['_id']

        # Ensure internship exists for this company
        job_data = c_info['internship']
        existing_job = internships_col.find_one({'company_id': str(c_id), 'title': job_data['title']})
        if not existing_job:
            job_doc = dict(job_data)
            job_doc['company_id'] = str(c_id)
            internships_col.insert_one(job_doc)

