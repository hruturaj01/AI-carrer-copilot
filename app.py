from flask import Flask, render_template, request, redirect, session
from db import Base, engine, SessionLocal
from ai import analyze_resume
import models
import PyPDF2
import docx
import json
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))

Base.metadata.create_all(bind=engine)


# Home Route
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")


# Sign up Route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    db = SessionLocal()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = db.query(models.User).filter_by(email=email).first()
        if existing_user:
            db.close()
            return "User already exists"

        user = models.User(email=email, password=password)
        db.add(user)
        db.commit()
        db.close()

        return redirect("/login")

    db.close()
    return render_template("signup.html")


# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    db = SessionLocal()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = db.query(models.User).filter_by(email=email, password=password).first()
        if user:
            session["user"] = user.email
            db.close()
            return redirect("/dashboard")
        else:
            db.close()
            return "Invalid credentials"

    db.close()
    return render_template("login.html")


# Dashboard Route
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")

    result = None

    if request.method == "POST":
        user_goal = request.form.get("role")
        resume_text = request.form.get("Resume") or ""
        file = request.files.get("file")

        # File Handling (PDF / DOCX)
        if file and file.filename != "":
            if file.filename.lower().endswith(".pdf"):
                try:
                    pdf_reader = PyPDF2.PdfReader(file)
                    extracted_text = ""
                    for page in pdf_reader.pages:
                        extracted_text += (page.extract_text() or "") + "\n"
                    resume_text = extracted_text
                except Exception as e:
                    result = {"error": f"PDF error : {str(e)}"}
            elif file.filename.lower().endswith(".docx"):
                try:
                    doc = docx.Document(file)
                    extracted_text = ""
                    for para in doc.paragraphs:
                        extracted_text += para.text + "\n"
                    resume_text = extracted_text
                except Exception as e:
                    result = {"error": f"Docx error :{str(e)}"}

        # AI Resume Analysis & Database Storage
        if resume_text and user_goal and not result:
            try:
                result = analyze_resume(resume_text, user_goal)

                db = SessionLocal()
                user = db.query(models.User).filter_by(email=session["user"]).first()

                if user:
                    report = models.Report(
                        user_id=user.id,
                        resume_text=resume_text,
                        result=json.dumps(result)
                    )
                    db.add(report)
                    db.commit()
                db.close()
            except Exception as e:
                result = {"error": f"AI error: {str(e)}"}

    return render_template(
        "dashboard.html",
        user=session["user"],
        result=result
    )


# History Route
@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")

    db = SessionLocal()
    user = db.query(models.User).filter_by(email=session["user"]).first()

    if not user:
        db.close()
        return redirect("/login")

    reports = db.query(models.Report).filter_by(user_id=user.id).all()

    # Convert JSON string back to dictionary for template rendering
    parsed_reports = []
    for r in reports:
        try:
            parsed_result = json.loads(r.result)
        except Exception:
            parsed_result = {}

        parsed_reports.append({
            "resume": r.resume_text,
            "result": parsed_result
        })

    db.close()
    return render_template("history.html", reports=parsed_reports)


# Logout Route
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)