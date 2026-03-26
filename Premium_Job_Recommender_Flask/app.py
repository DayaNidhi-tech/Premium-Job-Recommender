from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import os

# Load environment variables
load_dotenv()

# Recommender imports
from recommender.model import recommend_jobs, build_company_stats, build_skill_stats
from recommender.utils import extract_skills_from_text
from recommender.models import db, User
from recommender.job_api import fetch_real_jobs

# Resume parser
from future.resume_parser.parser import parse_pdf

# MongoDB
from future.database.db import applications_col


# ---------------- APP CONFIG ---------------- #

app = Flask(__name__)
app.secret_key = "super-secret-key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///premium_job_recommender.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


with app.app_context():
    db.create_all()


DATA_PATH = "jobs.csv"


def load_jobs():
    df = pd.read_csv(DATA_PATH)
    df.fillna("", inplace=True)
    return df


# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- DASHBOARD ---------------- #

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():

    if request.method == "POST":

        skills = request.form.get("skills", "").strip()
        experience = request.form.get("experience", "0").strip()
        location = request.form.get("location", "").strip()
        preference = request.form.get("preference", "").strip()
        job_type = request.form.get("job_type", "").strip()

        if not skills:
            flash("Skills field cannot be empty.", "danger")
            return redirect(url_for("dashboard"))

        try:
            exp_val = int(experience)
        except:
            exp_val = 0

        # Local CSV recommendations
        df = load_jobs()
        local_results = recommend_jobs(
            df=df,
            skills=skills,
            experience_years=exp_val,
            location=location,
            preference=preference,
            job_type=job_type,
            top_n=5
        )

        # Real API jobs (Adzuna)
        api_results = fetch_real_jobs(skills, location)

        # Merge results
        results = local_results + api_results

        # Save skills
        current_user.saved_skills = skills
        db.session.commit()

        return render_template("results.html", results=results, skills=skills)

    return render_template("dashboard.html", saved_skills=current_user.saved_skills or "")


# ---------------- COMPANIES ---------------- #

@app.route("/companies")
@login_required
def companies():
    df = load_jobs()
    stats = build_company_stats(df)
    return render_template("companies.html", companies=stats)


# ---------------- ANALYSIS ---------------- #

@app.route("/analysis")
@login_required
def analysis():
    df = load_jobs()
    stats = build_skill_stats(df)
    return render_template("analysis.html", skill_stats=stats)


# ---------------- APPLY ---------------- #

@app.route("/apply", methods=["POST"])
@login_required
def apply_job():

    job_title = request.form.get("job_title")
    company = request.form.get("company")
    apply_link = request.form.get("apply_link")

    if not job_title or not company:
        flash("Invalid job data.", "danger")
        return redirect(url_for("dashboard"))

    # Prevent duplicate application
    existing = applications_col.find_one({
        "user_id": current_user.id,
        "job_title": job_title,
        "company": company
    })

    if not existing:
        applications_col.insert_one({
            "user_id": current_user.id,
            "user_email": current_user.email,
            "job_title": job_title,
            "company": company,
            "applied_at": datetime.utcnow(),
            "status": "Redirected"
        })

    # Redirect to real job page
    if apply_link:
        return redirect(apply_link)

    return redirect(url_for("dashboard"))


# ---------------- AUTH ---------------- #

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("dashboard"))

        flash("Invalid credentials", "danger")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for("signup"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered", "danger")
            return redirect(url_for("signup"))

        new_user = User(
            email=email,
            password_hash=generate_password_hash(password),
            saved_skills=""
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Account created. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


# ---------------- RESUME PARSER ---------------- #

@app.route("/parse_resume", methods=["POST"])
@login_required
def parse_resume():

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    try:
        full_text = parse_pdf(file.stream)

        if not full_text.strip():
            return jsonify({'error': 'No readable text found'}), 400

        skills_list = extract_skills_from_text(full_text)

        return jsonify({'skills': ", ".join(skills_list)})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(debug=True)