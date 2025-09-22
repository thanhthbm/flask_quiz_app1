from datetime import datetime
import random
from flask import render_template, request, redirect, url_for, flash, session, g
from . import bp
from ...models import Subject, Question, QuizRecord, QuizAnswer
from ...extensions import db
from ...utils.auth import login_required

@bp.route('/', methods=['GET', 'POST'])
@login_required
def select():
    subjects = Subject.query.all()
    if request.method == 'POST':
        subject_id = int(request.form.get('subject_id'))
        k = max(1, int(request.form.get('number_of_questions', 1)))
        questions = Question.query.filter_by(subject_id=subject_id, is_deleted=False).all()
        if not questions:
            flash("No questions found.", "danger")
            return render_template('quiz/select.html', subjects=subjects)
        sample = random.sample(questions, min(k, len(questions)))
        qids = [q.id for q in sample]

        record = QuizRecord(user_id=g.user.id, subject_id=subject_id)
        db.session.add(record)
        db.session.flush()  # to get record.id

        session['quiz_record_id'] = record.id
        session['current_qids'] = qids
        return redirect(url_for('quiz.start'))

    return render_template('quiz/select.html', subjects=subjects)

@bp.route('/start', methods=['GET', 'POST'])
@login_required
def start():
    qids = session.get('current_qids', [])
    questions = Question.query.filter(Question.id.in_(qids)).all()
    if request.method == 'POST':
        record_id = session.get('quiz_record_id')
        score = 0
        for q in questions:
            ans = request.form.get(f"q_{q.id}", "").upper()
            correct = ans == q.correct_answer
            qa = QuizAnswer(quiz_record_id=record_id, question_id=q.id, answer=ans, is_correct=correct)
            db.session.add(qa)
            score += int(correct)

        record = QuizRecord.query.get(record_id)
        record.score = score
        record.end_time = datetime.utcnow()
        db.session.commit()

        return redirect(url_for('quiz.result', record_id=record_id))

    return render_template('quiz/start.html', questions=questions)

@bp.route('/result/<int:record_id>')
@login_required
def result(record_id):
    record = QuizRecord.query.get_or_404(record_id)
    answers = QuizAnswer.query.filter_by(quiz_record_id=record_id).all()
    time_taken = record.end_time - record.start_time if record.end_time else None
    return render_template('quiz/result.html',
                           quiz_record=record,
                           quiz_answers=answers,
                           time_taken=time_taken)
