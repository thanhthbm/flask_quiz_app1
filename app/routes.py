from flask import render_template, redirect, url_for, flash
from app import app, db
from app.forms import RegistrationForm, LoginForm, AddSubjectForm, AddQuestionForm
from app.models import Subject

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Process registration
        flash('Registration successful.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Process login
        flash('Login successful.')
        return redirect(url_for('home'))
    return render_template('login.html', form=form)

@app.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    form = AddSubjectForm()
    if form.validate_on_submit():
        # Process adding subject
        flash('Subject added successfully.')
        return redirect(url_for('add_subject'))
    return render_template('add_subject.html', form=form)

@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    form = AddQuestionForm()
    form.subject_id.choices = [(subject.id, subject.name) for subject in Subject.query.all()]
    if form.validate_on_submit():
        # Process adding question
        flash('Question added successfully.')
        return redirect(url_for('add_question'))
    return render_template('add_question.html', form=form)
