import os, json
from datetime import datetime
from functools import wraps
from datetime import timedelta
from idlelib.iomenu import encoding

from flask import render_template, redirect, url_for, flash, session, g, request
from werkzeug.utils import secure_filename

from app import app, db, process_csv, process_json
from app.forms import RegistrationForm, LoginForm, AddSubjectForm, AddQuestionForm, QuizForm
from app.models import Subject, User, Question, QuizRecord, QuizAnswer

@app.template_filter('format_time')
def format_time(delta):
    if delta:
        hours, remainder = divmod(delta.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
    return "00:00:00"

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['txt', 'json']

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
    subjects = Subject.query.all()

    if request.method == 'POST':
        input_method = request.form.get('input_method')
        subject_id = request.form.get('subject_id')

        if not subject_id:
            flash("Please select a subject", "danger")
            return render_template('add_question.html', subjects=subjects)

        if input_method == 'manual':
            # Xử lý manual input như cũ
            content = request.form.get('content')
            option_a = request.form.get('option_a')
            option_b = request.form.get('option_b')
            option_c = request.form.get('option_c')
            option_d = request.form.get('option_d')
            correct_answer = request.form.get('correct_answer')

            if not all([content, option_a, option_b, option_c, option_d, correct_answer]):
                flash("Please fill in all fields for manual entry.", "danger")
            else:
                try:
                    question = Question(
                        subject_id=subject_id,
                        content=content,
                        option_a=f"A. {option_a}" if not option_a.startswith('A.') else option_a,
                        option_b=f"B. {option_b}" if not option_b.startswith('B.') else option_b,
                        option_c=f"C. {option_c}" if not option_c.startswith('C.') else option_c,
                        option_d=f"D. {option_d}" if not option_d.startswith('D.') else option_d,
                        correct_answer=correct_answer.upper()
                    )
                    db.session.add(question)
                    db.session.commit()
                    flash("Question added successfully!", "success")
                    return redirect(url_for('add_question'))
                except Exception as e:
                    db.session.rollback()
                    flash(f"Error adding question: {str(e)}", "danger")

        elif input_method == 'file':
            if 'file' not in request.files:
                flash('No file uploaded', 'danger')
                return render_template('add_question.html', subjects=subjects)

            file = request.files['file']
            if file.filename == '':
                flash('No file selected', 'danger')
                return render_template('add_question.html', subjects=subjects)

            if not allowed_file(file.filename):
                flash('Invalid file type. Please upload .txt or .json file', 'danger')
                return render_template('add_question.html', subjects=subjects)

            try:
                if file.filename.endswith('.txt'):
                    process_txt_file(file, subject_id)
                elif file.filename.endswith('.json'):
                    process_json_file(file, subject_id)
                return redirect(url_for('add_question'))
            except Exception as e:
                db.session.rollback()
                flash(f"Error processing file: {str(e)}", "danger")

    return render_template('add_question.html', subjects=subjects)


def process_txt_file(file, subject_id):
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    file_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
    try:
        file.save(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    parts = line.strip().split('|')
                    if len(parts) != 6:
                        flash(f"Error on line {line_num}: Invalid format", "danger")
                        continue

                    content = parts[0].strip()
                    options = {
                        "A": parts[1].strip(),
                        "B": parts[2].strip(),
                        "C": parts[3].strip(),
                        "D": parts[4].strip()
                    }
                    correct_answer = parts[5].strip().upper()

                    if correct_answer not in ["A", "B", "C", "D"]:
                        flash(f"Error on line {line_num}: Invalid correct answer", "danger")
                        continue

                    for key in options:
                        if not options[key].startswith(f"{key}. "):
                            options[key] = f"{key}. {options[key]}"

                    question = Question(
                        subject_id=subject_id,
                        content=content,
                        option_a=options["A"],
                        option_b=options["B"],
                        option_c=options["C"],
                        option_d=options["D"],
                        correct_answer=correct_answer
                    )
                    db.session.add(question)
                except Exception as e:
                    flash(f"Error on line {line_num}: {str(e)}", "danger")
                    continue

        db.session.commit()
        flash("Questions added successfully from .txt file!", "success")
    except Exception as e:
        raise e
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


def process_json_file(file, subject_id):
    try:
        data = json.loads(file.read().decode('utf-8'))
        if not isinstance(data, list):
            flash("JSON file must contain an array of questions", "danger")
            return

        for index, item in enumerate(data):
            try:
                content = item.get('content', '').strip()
                option_a = item.get('option_a', '').strip()
                option_b = item.get('option_b', '').strip()
                option_c = item.get('option_c', '').strip()
                option_d = item.get('option_d', '').strip()
                correct_answer = item.get('correct_answer', '').strip().upper()

                if not all([content, option_a, option_b, option_c, option_d, correct_answer]):
                    flash(f"Error on question {index + 1}: Missing required fields", "danger")
                    continue

                if correct_answer not in ["A", "B", "C", "D"]:
                    flash(f"Error on question {index + 1}: Invalid correct answer", "danger")
                    continue

                options = {
                    "A": option_a,
                    "B": option_b,
                    "C": option_c,
                    "D": option_d
                }
                for key in options:
                    if not options[key].startswith(f"{key}. "):
                        options[key] = f"{key}. {options[key]}"

                question = Question(
                    subject_id=subject_id,
                    content=content,
                    option_a=options["A"],
                    option_b=options["B"],
                    option_c=options["C"],
                    option_d=options["D"],
                    correct_answer=correct_answer
                )
                db.session.add(question)
            except Exception as e:
                flash(f"Error on question {index + 1}: {str(e)}", "danger")
                continue

        db.session.commit()
        flash("Questions added successfully from JSON file!", "success")
    except json.JSONDecodeError:
        flash("Invalid JSON format", "danger")
    except Exception as e:
        raise e


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