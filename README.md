# AI-carrer-copilot
An AI-powered career assistant that analyzes resumes against target job roles, identifies skill gaps, and provides actionable feedback to help users land their next role.
# 🚀 AI Career Copilot

**AI Career Copilot** is a full-stack web application that acts as an intelligent career advisor. Users can upload their resumes, specify a target job role, and receive instant, AI-driven evaluations—complete with ATS compatibility insights, skill-gap analysis, and actionable recommendations to improve their job readiness.

---

## ✨ Key Features

* **📄 Smart Resume Analysis:** Upload and parse resumes to extract key skills, experience, and qualifications.
* **🎯 Target Role Matching:** Evaluates how well a resume aligns with a user's desired job title or description.
* **🔍 Skill-Gap & ATS Insights:** Highlights missing keywords, technical gaps, and formatting improvements.
* **🔐 User Authentication:** Secure registration and login system to protect user data.
* **📊 Evaluation History:** Tracks past resume submissions and AI feedback so users can monitor improvements over time.

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask
* **Frontend:** HTML5, CSS3, Jinja2 Templates
* **Database:** TiDB (MySQL-compatible distributed SQL)
* **AI Integration:** Generative AI API (LLM-powered resume evaluation)
* **Environment Management:** `python-dotenv`

---


## 📂 Project Structure

```text
ai-career-copilot/
├── app.py               # Main Flask application & route handlers
├── ai.py                # AI API integration & prompt evaluation logic
├── db.py                # TiDB database connection setup
├── models.py            # Database models & query functions
├── requirements.txt     # Python dependencies
├── .env.example         # Template for environment variables
├── static/              # CSS stylesheets, scripts, and assets
└── templates/           # HTML templates (base.html, dashboard, login, etc.)
