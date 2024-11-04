from werkzeug.security import generate_password_hash, check_password_hash
from app import db, app
from flask_security import UserMixin, RoleMixin
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

class User(UserMixin, db.Model):
    __tablename__: 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable = False, unique=True)
    email = db.Column(db.String(200), nullable = False, unique = True)
    password_hash = db.Column(db.String(128), nullable = False)
    role = db.relationship('Role', uselist = False, back_populates = 'user')


    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('user', back_populates = 'role')


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)

    #4 answers
    option_a = db.Column(db.String(500), nullable=False)
    option_b = db.Column(db.String(500), nullable=False)
    option_c = db.Column(db.String(500), nullable=False)
    option_d = db.Column(db.String(500), nullable=False)

    #right answer: A, B, C, D
    correct_answer = db.Column(db.String(1), nullable=False)
    subject = db.relationship('Subject', back_populates = 'questions')

    def __repr__(self):
        return '<Question {}>'.format(self.id)

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    #one-to-many relationship with Subject
    questions = db.relationship('Question', back_populates = 'subject')

    def __repr__(self):
        return '<Subject {}>'.format(self.name)

