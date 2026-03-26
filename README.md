# Premium Job Recommender (CareerNavi Pro)

A full-stack Flask-based job recommendation system that suggests relevant jobs based on user skills, parses resumes, and allows users to apply directly.

---

## Features

* Smart Job Recommendation
  Suggests jobs based on skills, experience, location, and preferences

* Resume Parser
  Extracts skills automatically from uploaded PDF resumes

* AI-based Matching
  Calculates job match percentage

* Company Insights
  Displays top hiring companies

* Skill Analysis
  Shows trending and in-demand skills

* Apply System
  Allows users to apply for jobs and prevents duplicate applications

* Authentication System
  Secure login and signup with password hashing

---

## Tech Stack

* Backend: Flask (Python)
* Database: SQLite and MongoDB
* Frontend: HTML, CSS, JavaScript (Jinja Templates)

Libraries used:

* pandas
* pdfplumber
* flask-login
* werkzeug

---

## Project Structure

```
Premium_Job_Recommender_Flask/
│
├── app.py
├── jobs.csv
├── templates/
├── static/
├── recommender/
│   ├── model.py
│   ├── utils.py
│   ├── job_api.py
│   └── models.py
│
├── future/
│   ├── database/
│   └── resume_parser/
│
└── instance/
```

---

## Installation and Setup

1. Clone the repository

```
git clone https://github.com/DayaNidhi-tech/Premium-Job-Recommender.git
cd Premium-Job-Recommender/Premium_Job_Recommender_Flask
```

2. Create a virtual environment

```
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies

```
pip install -r requirements.txt
```

4. Run the application

```
python app.py
```

5. Open in browser

```
http://127.0.0.1:5000
```

---

## Key Highlights

* Integrated real-time job API
* Resume parsing using pdfplumber
* Clean UI with match percentage visualization
* Duplicate application prevention
* Proper Git workflow with branching and pull requests

---

## Future Improvements

* Deployment to cloud platforms (Render, Railway)
* Advanced AI-based recommendation system
* Enhanced analytics dashboard
* Email notification system

---

## Author

DayaNidhi
GitHub: https://github.com/DayaNidhi-tech

---

## License

This project is for educational and development purposes.
