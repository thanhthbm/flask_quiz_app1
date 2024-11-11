from datetime import datetime
from functools import wraps
from datetime import timedelta
from flask import render_template, redirect, url_for, flash, session, g, request

from app import app, db
from app.forms import RegistrationForm, LoginForm, AddSubjectForm, AddQuestionForm, QuizForm
from app.models import Subject, User, Question, QuizRecord, QuizAnswer

@app.template_filter('format_time')
def format_time(delta):
    if delta:
        hours, remainder = divmod(delta.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
    return "00:00:00"


def login_required(f):
    @wraps(f)

    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def requires_roles(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.user is None or g.user.role not in roles:
                flash('You do not have permission to access this page.')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            session['role'] = user.role
            flash('You are now logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        session['role'] = user.role
        flash('You are now registered.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    session.pop('user_id', None)
    session.pop('role', None)
    flash('You are now logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/add_subject', methods=['GET', 'POST'])
@requires_roles('admin')
def add_subject():
    form = AddSubjectForm()
    if form.validate_on_submit():
        subject = Subject(name=form.name.data)
        db.session.add(subject)
        db.session.commit()

        flash('Subject add successfully', 'success')

        form.name.data = ''
        return redirect(url_for('add_subject'))
    return render_template('add_subject.html', form=form)

@app.route('/add_question', methods=['GET', 'POST'])
@requires_roles('admin')
def add_question():
    form = AddQuestionForm()

    subjects = Subject.query.filter_by(is_deleted=False).all()
    form.subject_id.choices = [(subject.id, subject.name) for subject in subjects]

    if form.validate_on_submit():
        new_question = Question(
            subject_id=form.subject_id.data,
            content=form.content.data,
            option_a = form.option_a.data,
            option_b = form.option_b.data,
            option_c = form.option_c.data,
            option_d = form.option_d.data,
            correct_answer = form.correct_answer.data,
        )

        db.session.add(new_question)
        db.session.commit()
        form.content.data = ''
        form.option_a.data = ''
        form.option_b.data = ''
        form.option_c.data = ''
        form.option_d.data = ''
        form.correct_answer.data = ''
        flash('Your question has been added.', 'success')
    return render_template('add_question.html', form=form)


@app.route('/start_quiz/<int:subject_id>/<int:number_of_questions>', methods=['GET', 'POST'])
@login_required
def start_quiz(subject_id, number_of_questions):
    all_questions = Question.query.filter_by(subject_id=subject_id, is_deleted = False).all()
    number_of_questions_available = min(number_of_questions, len(all_questions))
    questions = Question.query.filter_by(subject_id=subject_id, is_deleted = False).limit(number_of_questions_available).all()
    if not questions:
        return "No questions available for this subject."

    if request.method == 'POST':
        quiz_record = QuizRecord(user_id=g.user.id, subject_id=subject_id, score=0)
        db.session.add(quiz_record)
        db.session.commit()


        for question in questions:
            selected_answer = request.form.get(f'question_{question.id}')
            is_correct = (selected_answer and selected_answer[0] == question.correct_answer)
            print(selected_answer[0])
            quiz_answer = QuizAnswer(
                quiz_record_id=quiz_record.id,
                question_id=question.id,
                answer=selected_answer,
                is_correct=is_correct
            )
            db.session.add(quiz_answer)

            if is_correct:
                quiz_record.score += 1

        quiz_record.end_time = datetime.utcnow()
        db.session.add(quiz_record)
        db.session.commit()

        return redirect(url_for('quiz_result', quiz_record_id=quiz_record.id))

    return render_template('start_quiz.html', questions=questions, subject_id=subject_id, number_of_questions=number_of_questions)



@app.route('/quiz_result/<int:quiz_record_id>', methods=['GET'])
@login_required
def quiz_result(quiz_record_id):
    quiz_record = QuizRecord.query.get(quiz_record_id)
    if quiz_record.end_time and quiz_record.start_time:
        time_taken = quiz_record.end_time - quiz_record.start_time
    else:
        time_taken = timedelta(0)

    hours, remainder = divmod(int(time_taken.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    time_taken_formatted = f"{hours:02}:{minutes:02}:{seconds:02}"

    subject_id = quiz_record.subject_id
    subject = Subject.query.get(subject_id)
    quiz_answers = QuizAnswer.query.filter_by(quiz_record_id=quiz_record_id).all()
    return render_template('quiz_result.html', quiz_record=quiz_record, quiz_answers=quiz_answers, subject=subject, time_taken_formatted=time_taken_formatted)

@app.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    form = QuizForm()
    subjects = Subject.query.filter_by(is_deleted=False).all()
    form.subject_id.choices = [(subject.id, subject.name) for subject in subjects]

    if form.validate_on_submit():
        subject_id = form.subject_id.data
        number_of_questions = form.number_of_questions.data

        return redirect(url_for('start_quiz', subject_id=subject_id, number_of_questions=number_of_questions))
    return render_template('quiz.html', form=form)

@app.route('/history', methods=['GET', 'POST'])
@login_required
def history():
    quiz_records = QuizRecord.query.filter_by(user_id=g.user.id).order_by(QuizRecord.start_time.desc()).all()
    return render_template('quiz_history.html', quiz_records=quiz_records)

@app.route('/leaderboard/<int:subject_id>', methods=['GET'])
@login_required
def leaderboard(subject_id):
    leaderboard_data = db.session.query(
        User.username,
        Subject.name.label('subject_name'),
        QuizRecord.score,
        QuizRecord.start_time
    ).join(QuizRecord, QuizRecord.user_id == User.id) \
     .join(Subject, QuizRecord.subject_id == Subject.id) \
     .filter(Subject.id == subject_id) \
     .order_by(QuizRecord.score.desc()) \
     .all()

    subject_name = db.session.query(Subject.name).filter(Subject.id == subject_id).scalar()

    return render_template('leaderboard.html', leaderboard_data=leaderboard_data, subject_name=subject_name)