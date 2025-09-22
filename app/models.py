from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    hashed_password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(80), nullable=False, default='student')  # 'admin' | 'student'
    is_locked = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password: str):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.hashed_password, password)

class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    questions = db.relationship('Question', backref='subject', lazy=True)

    def __repr__(self):
        return f"<Subject {self.name}>"

class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(250), nullable=False)
    option_a = db.Column(db.String(250), nullable=False)
    option_b = db.Column(db.String(250), nullable=False)
    option_c = db.Column(db.String(250), nullable=False)
    option_d = db.Column(db.String(250), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)  # 'A'/'B'/'C'/'D'
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

    def __repr__(self):
        return f"<Question {self.id}>"

class QuizRecord(db.Model):
    __tablename__ = 'quiz_record'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Integer, nullable=False, default=0)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relationship('User', backref='quiz_records', lazy=True)
    subject = db.relationship('Subject', backref='quiz_records', lazy=True)

    def __repr__(self):
        return f"<QuizRecord {self.id}>"

class QuizAnswer(db.Model):
    __tablename__ = 'quiz_answer'
    id = db.Column(db.Integer, primary_key=True)
    quiz_record_id = db.Column(db.Integer, db.ForeignKey('quiz_record.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    answer = db.Column(db.String(1), nullable=False)  # 'A'/'B'/'C'/'D'
    is_correct = db.Column(db.Boolean, nullable=False, default=False)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    quiz_record = db.relationship('QuizRecord', backref='quiz_answers', lazy=True)
    question = db.relationship('Question', backref='quiz_answers', lazy=True)

    def __repr__(self):
        return f"<QuizAnswer {self.id}>"
