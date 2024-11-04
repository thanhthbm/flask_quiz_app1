from app import app
from flask import render_template, request, redirect, url_for, session, g, flash
from app.forms import LoginForm, RegistrationForm, QuestionForm, SubjectForm
from app.models import User, Subject, Question
from app import db
from flask_user import current_user, login_required, roles_required
from flask_login import login_user, logout_user, current_user


@app.before_request
def load_logged_user():
    g.user = current_user


@app.route('/')
def home():
    return render_template('index.html', title='Home')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('admin_dashboard'))  # Redirect to the admin dashboard or home
        else:
            flash('Invalid username or password')

    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/admin/add_subject', methods=['GET', 'POST'])
@login_required
def add_subject():
    form = SubjectForm()
    if form.validate_on_submit():
        new_subject = Subject(name=form.name.data)
        db.session.add(new_subject)
        db.session.commit()

        flash('Subject Added Successfully', 'success')
        return redirect(url_for('add_subject'))

    return render_template('add_subject.html', title='Add Subject', form=form)


@app.route('/admin/add_question', methods=['GET', 'POST'])
@login_required
def add_question():
    form = QuestionForm()
    form.subject_id.choices = [(subject.id, subject.name) for subject in Subject.query.all()]
    if form.validate_on_submit():
        question = Question(
            content=form.content.data,
            option_a=form.option_a.data,
            option_b=form.option_b.data,
            option_c=form.option_c.data,
            option_d=form.option_d.data,
            correct_answer=form.correct_answer.data,
            subject_id=form.subject_id.data
        )
        db.session.add(question)
        db.session.commit()
        flash('Question Added Successfully', 'success')
        return redirect(url_for('add_question'))
    return render_template('add_question.html', title='Add Question', form=form)

@app.route('/admin/dashboard', methods=['GET'])
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html', title='Admin Dashboard')
