from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    hashed_password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(80), nullable=False, default='student')

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)





class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    questions = db.relationship('Question', backref='subject', lazy=True)

    def __repr__(self):
        return '<Subject %r>' % self.name


class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(250), nullable=False)
    option_a = db.Column(db.String(250), nullable=False)
    option_b = db.Column(db.String(250), nullable=False)
    option_c = db.Column(db.String(250), nullable=False)
    option_d = db.Column(db.String(250), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)

    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    def __repr__(self):
        return '<Question %r>' % self.content

class QuizAnswer(db.Model):
    __tablename__ = 'quiz_answer'
    id = db.Column(db.Integer, primary_key=True)
