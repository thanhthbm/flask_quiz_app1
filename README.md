# Flask Quiz App

A minimal quiz platform built with Flask. Users can register, login, take quizzes by subject, see results & leaderboard. Admins can manage subjects and questions, including bulk import via file upload.

---

## 📌 Features

- 👤 User registration, login, logout
- 🔐 Role-based access control (Admin vs Student)
- 📝 Take quizzes by subject with configurable number of questions and duration
- 📊 View quiz results with correct/incorrect feedback
- 📚 View quiz history and leaderboard
- 🛠️ Admin Panel:
  - Add subjects
  - Add/edit/delete/restore questions
  - Bulk import from `.txt`, `.csv`, `.json`
  - Filter, search, and batch actions

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask  
- **ORM**: SQLAlchemy  
- **Frontend**: HTML/CSS (Jinja2), JavaScript  
- **Forms**: Flask-WTF  
- **Database Migrations**: Flask-Migrate  
- **Deployment**: Vercel-compatible  

---

## 🚀 Getting Started

### 📦 Prerequisites

- Python 3.7+
- SQLite or any SQLAlchemy-supported database
- `pip`, `virtualenv`, or `venv`

### 🔧 Installation

```bash
git clone <repo-url>
cd flask_quiz_app1

python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

pip install -r requirements.txt
```

### 🔨 Database Setup
```bash
flask db init
flask db migrate
flask db upgrade
```

### Create Admin User
```bash
flask seed-admin
# Default: username=admin, password=admin123
```

### Run the app
``` bash
set FLASK_APP=run.py
set FLASK_ENV=development
flask run
```