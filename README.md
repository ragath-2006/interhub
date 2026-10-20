# InternHub - AI-Powered Student Internship & Career Portal (MongoDB Edition)

**InternHub** is a comprehensive full-stack web application built on **Flask** and **MongoDB**, designed for students, tech employers, and academic institutions. It features an intelligent **TF-IDF Vectorizer + Cosine Similarity** resume-to-job matching engine, a **Random Forest Classifier** for recruitment shortlisting prediction, a **Single Dynamic Resume Builder**, real-time notifications, and a **verified review system** guarded by internship completion status.

---

## 🚀 Key Features

### 1. 🎓 Student Portal
- **Single Dynamic Resume Builder**:
  - Live unified resume editor (Personal bio, contact, CGPA, Education history, Projects, Experience, Certifications, Technical & Soft skills).
  - Print & PDF-ready export layout.
  - Stored dynamically as structured document objects in MongoDB.
  - Changes instantly update AI recommendation vectors and all active applications.
- **AI-Powered Internship Recommendations**:
  - Automatically vectorizes student profile text and calculates **TF-IDF Cosine Similarity** with job specs.
  - Predicts **Random Forest Shortlist Likelihood (%)** using student CGPA, projects count, certifications, and skill match overlap.
  - Visual breakdown of **Matched Skills** vs. **Missing Skills**.
- **Application Tracking & Status Lifecycle**:
  - Real-time status updates: `Applied` $\rightarrow$ `Under Review` $\rightarrow$ `Shortlisted` $\rightarrow$ `Selected` $\rightarrow$ `Completed` / `Rejected`.
- **Verified Review Policy**:
  - Students can browse all company ratings publicly.
  - **Review submission is strictly unlocked ONLY when an internship is marked as `Completed`** by the employer.

### 2. 🏢 Employer / Company Portal
- **Internship Management**:
  - Post detailed internships with domains, required skills, stipend, work mode (Remote/Hybrid/On-site), duration, and deadlines into MongoDB.
  - Automatic broadcast notification to students whose skills match the new posting.
- **Candidate Screening & AI Ranking**:
  - Applicant directory sorted by **TF-IDF Match %**, **Random Forest Probability %**, or **CGPA**.
  - Interactive Dynamic Resume modal view with skill overlap analysis.
  - Multi-stage status updater with custom feedback notes sent directly to candidates.
- **Company Reviews**:
  - View verified student feedback and ratings across Work Environment, Learning, and Mentorship.

### 3. 🛡️ Administrator Panel
- Enterprise employer verification & moderation.
- Platform analytics: total students, companies, active internships, applications, and verified reviews.

### 4. 🌐 Public Landing & Exploration Pages
- Modern responsive glassmorphism UI.
- Keyword and multi-filter search (Domain, Location, Stipend, Work Mode).
- Public company reviews and transparent ratings.

---

## 🍃 MongoDB Schema & Collections

InternHub uses **MongoDB** (`mongodb://localhost:27017/internhub_db` or MongoDB Atlas via `MONGO_URI`):

| Collection | Description | Document Structure Highlights |
| :--- | :--- | :--- |
| `users` | User credentials & roles | `_id`, `email`, `password_hash`, `role` ('student', 'company', 'admin'), `is_active`, `created_at` |
| `students` | Single Dynamic Resume profiles | `_id`, `user_id`, `full_name`, `cgpa`, `technical_skills`, `soft_skills`, `educations: [...]`, `projects: [...]`, `experiences: [...]`, `certifications: [...]` |
| `companies` | Employer organization profiles | `_id`, `user_id`, `company_name`, `industry`, `location`, `website`, `is_verified` |
| `internships` | Job postings | `_id`, `company_id`, `title`, `domain`, `required_skills`, `stipend`, `work_mode`, `is_active`, `deadline` |
| `applications`| Recruitment lifecycle records | `_id`, `internship_id`, `student_id`, `status`, `tfidf_score`, `rf_probability`, `cover_letter`, `company_notes` |
| `reviews` | Verified completed intern reviews | `_id`, `company_id`, `student_id`, `rating`, `work_environment_rating`, `learning_rating`, `mentor_support_rating`, `title`, `review_text` |
| `notifications`| Live user alert feed | `_id`, `user_id`, `title`, `message`, `category`, `link`, `is_read`, `created_at` |

---

## 🧠 AI / Machine Learning Engine

| Component | Technique / Model | Purpose |
| :--- | :--- | :--- |
| **Skill & Resume Match** | `TfidfVectorizer` + `Cosine Similarity` | Vectorizes resume & job description text into TF-IDF embeddings to compute semantic similarity $(0-100\%)$ |
| **Shortlist Prediction** | `RandomForestClassifier` (Scikit-Learn) | Predicts candidate shortlisting probability based on TF-IDF similarity, CGPA, projects, certifications, and experience |
| **Skill Overlap** | Natural Language Keyword Matching | Extracts exact matched required skills vs missing skills for targeted candidate upskilling |

---

## 🔑 Pre-Configured Demo Credentials

Log in directly or use the 1-click demo buttons on the [Login Page](http://127.0.0.1:5000/login):

| Role | Email | Password | Details |
| :--- | :--- | :--- | :--- |
| **Student** | `student@internhub.com` | `student123` | **Rahul Sharma** (NIT CSE, CGPA 8.85, Dynamic Resume + Completed Internship at Swiggy with Verified Review) |
| **Employer** | `hr@google.com` | `company123` | **Google India Tech** (AI/ML Research Internships & Applicants) |
| **Employer** | `talent@microsoft.com` | `company123` | **Microsoft IDC** (Full Stack Software Engineering) |
| **Employer** | `careers@swiggy.in` | `company123` | **Swiggy Engineering** (Backend Systems & Data Analytics) |
| **Admin** | `admin@internhub.com` | `admin123` | **Platform Governance & Company Verification** |

---

## 🛠️ How to Run the Application

### 1. Prerequisites
- Python 3.10+
- MongoDB (running locally on `mongodb://localhost:27017` or configured via `MONGO_URI` for MongoDB Atlas)

### 2. Install Dependencies
```bash
pip install flask pymongo scikit-learn numpy werkzeug mongomock
```

### 3. (Optional) Configure MongoDB URI
If using MongoDB Atlas or a remote server, set the environment variable:
```powershell
$env:MONGO_URI = "mongodb+srv://<username>:<password>@cluster0.mongodb.net/internhub_db"
```
*(Defaults to `mongodb://localhost:27017/internhub_db` with automatic fallback)*

### 4. Launch the Server
```bash
python app.py
```

### 5. Open in Browser
Navigate to **`http://127.0.0.1:5000`** in your web browser.
