from datetime import datetime
import random
from flask import render_template, request, redirect, url_for, flash, session, g, abort
from . import bp
from ...models import Subject, Question, QuizRecord, QuizAnswer
from ...extensions import db
from ...utils.auth import login_required

@bp.route('/', methods=['GET', 'POST'])
@login_required
def select():
    subjects = Subject.query.order_by(Subject.name.asc()).all()

    if request.method == 'POST':
        try:
            subject_id = int(request.form.get('subject_id', '').strip())
        except (TypeError, ValueError):
            flash("Invalid subject.", "danger")
            return render_template('quiz/select.html', subjects=subjects)

        try:
            k = int(request.form.get('number_of_questions', 1))
            k = max(1, k)
        except (TypeError, ValueError):
            k = 1

        questions = (
            Question.query
            .filter_by(subject_id=subject_id, is_deleted=False)
            .all()
        )
        if not questions:
            flash("No questions found for this subject.", "danger")
            return render_template('quiz/select.html', subjects=subjects)

        sample = random.sample(questions, min(k, len(questions)))
        qids = [q.id for q in sample]

        record = QuizRecord(user_id=g.user.id, subject_id=subject_id, start_time=datetime.utcnow())
        db.session.add(record)
        db.session.flush()

        session['quiz_record_id'] = record.id
        session['current_qids'] = qids
        session['quiz_locked'] = False

        db.session.commit()

        return redirect(url_for('quiz.start'))

    return render_template('quiz/select.html', subjects=subjects)


@bp.route('/start', methods=['GET', 'POST'])
@login_required
def start():
    record_id = session.get('quiz_record_id')
    qids = session.get('current_qids') or []

    # Nếu thiếu context => quay lại chọn
    if not record_id or not qids:
        flash("Quiz session not found. Please select again.", "warning")
        return redirect(url_for('quiz.select'))

    questions_by_id = {q.id: q for q in Question.query.filter(Question.id.in_(qids)).all()}
    questions = [questions_by_id[qid] for qid in qids if qid in questions_by_id]

    if not questions:
        flash("Questions not available anymore.", "danger")
        return redirect(url_for('quiz.select'))

    if request.method == 'POST':
        if session.get('quiz_locked'):
            flash("This quiz submission was already processed.", "info")
            return redirect(url_for('quiz.result', record_id=record_id))

        record = QuizRecord.query.get_or_404(record_id)
        if record.user_id != g.user.id:
            abort(403)

        existing_count = QuizAnswer.query.filter_by(quiz_record_id=record_id).count()
        if existing_count > 0:
            session['quiz_locked'] = True
            flash("This quiz submission was already processed.", "info")
            return redirect(url_for('quiz.result', record_id=record_id))

        score = 0
        for q in questions:
            raw = request.form.get(f"q_{q.id}", "")
            ans = (raw or "").strip().upper()
            if ans not in {"A", "B", "C", "D"}:
                ans = ""
            correct = (ans == (q.correct_answer or "").upper())
            qa = QuizAnswer(
                quiz_record_id=record_id,
                question_id=q.id,
                answer=ans,
                is_correct=correct
            )
            db.session.add(qa)
            score += int(bool(correct))

        record.score = score
        record.end_time = datetime.utcnow()
        db.session.commit()

        session['quiz_locked'] = True
        session.pop('current_qids', None)

        return redirect(url_for('quiz.result', record_id=record_id))

    return render_template('quiz/start.html', questions=questions)


@bp.route('/result/<int:record_id>')
@login_required
def result(record_id):
    record = QuizRecord.query.get_or_404(record_id)
    if record.user_id != g.user.id:
        abort(403)

    answers = QuizAnswer.query.filter_by(quiz_record_id=record_id).all()

    time_taken = None
    if record.end_time and record.start_time:
        time_taken = record.end_time - record.start_time

    if session.get('quiz_record_id') == record_id:
        session.pop('quiz_record_id', None)

    return render_template(
        'quiz/result.html',
        quiz_record=record,
        quiz_answers=answers,
        time_taken=time_taken
    )
