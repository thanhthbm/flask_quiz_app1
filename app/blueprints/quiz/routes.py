from datetime import datetime, timedelta
import random
from flask import render_template, request, redirect, url_for, flash, session, \
  g, abort, current_app
from sqlalchemy import desc, func

from . import bp
from ...models import Subject, Question, QuizRecord, QuizAnswer, User
from ...extensions import db
from ...utils.auth import login_required

# -------- Helpers --------

def _shuffle_question(q: Question):
    original = [
        ('A', q.option_a),
        ('B', q.option_b),
        ('C', q.option_c),
        ('D', q.option_d),
    ]
    random.shuffle(original)
    remapped = []
    correct_letter = q.correct_answer
    new_correct = None
    letters = ['A', 'B', 'C', 'D']
    for idx, (_orig_letter, text) in enumerate(original):
        new_letter = letters[idx]
        remapped.append((new_letter, text))
        if _orig_letter == correct_letter:
            new_correct = new_letter
    return remapped, new_correct


def _quiz_session_key(record_id: int) -> str:
    return f"quiz_{record_id}"


# -------- Routes --------

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

        try:
            dur_min = int(request.form.get('duration_minutes') or 0)
        except (TypeError, ValueError):
            dur_min = 0
        if dur_min <= 0:
            dur_min = current_app.config.get("QUIZ_DURATION_MINUTES_DEFAULT", 15)

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

        # Tạo QuizRecord
        record = QuizRecord(
            user_id=g.user.id,
            subject_id=subject_id,
            start_time=datetime.utcnow(),
            score=0
        )
        db.session.add(record)
        db.session.flush()

        session['quiz_record_id'] = record.id
        session['current_qids'] = qids
        session['quiz_locked'] = False
        session['quiz_duration_min'] = int(dur_min)

        db.session.commit()

        return redirect(url_for('quiz.start_quiz'))

    return render_template('quiz/select.html', subjects=subjects)


@bp.route('/start', methods=['GET'])
@login_required
def start_quiz():

    record_id = session.get('quiz_record_id')
    qids = session.get('current_qids')
    duration_min = session.get('quiz_duration_min')

    if record_id and qids:
        record = QuizRecord.query.get_or_404(record_id)
        if record.user_id != g.user.id:
            abort(403)

        subject = Subject.query.get_or_404(record.subject_id)
        questions = Question.query.filter(Question.id.in_(qids)).all()
        if not questions:
            flash("No questions selected.", "warning")
            return redirect(url_for("quiz.select"))

        # nếu chưa có duration thì dùng config
        if not duration_min or duration_min <= 0:
            duration_min = current_app.config.get("QUIZ_DURATION_MINUTES_DEFAULT", 15)

    else:
        subject_id = request.args.get("subject_id", type=int)
        if not subject_id:
            flash("Missing subject_id", "danger")
            return redirect(url_for("main.index"))

        subject = Subject.query.get_or_404(subject_id)

        n = request.args.get(
            "n",
            default=current_app.config.get("QUIZ_NUM_QUESTIONS_DEFAULT", 10),
            type=int,
        )
        duration_min = request.args.get(
            "dur",
            default=current_app.config.get("QUIZ_DURATION_MINUTES_DEFAULT", 15),
            type=int,
        )

        questions = (
            Question.query.filter_by(subject_id=subject_id, is_deleted=False)
            .order_by(func.random())
            .limit(n)
            .all()
        )
        if not questions:
            flash("Subject has no question.", "warning")
            return redirect(url_for("main.index"))

        record = QuizRecord(
            user_id=g.user.id,
            subject_id=subject_id,
            start_time=datetime.utcnow(),
            score=0,
        )
        db.session.add(record)
        db.session.flush()

        qids = [q.id for q in questions]
        session['quiz_record_id'] = record.id
        session['current_qids'] = qids
        session['quiz_locked'] = False
        session['quiz_duration_min'] = int(duration_min)

        db.session.commit()

    maps = {}
    q_compact = []
    for q in questions:
        opts, new_correct = _shuffle_question(q)
        maps[q.id] = {"opts": opts, "correct": new_correct}
        q_compact.append({"id": q.id, "content": q.content, "opts": opts})

    quiz_key = _quiz_session_key(record.id)
    session[quiz_key] = {
        "subject_id": subject.id,
        "duration_min": int(duration_min),
        "start_utc": record.start_time.isoformat(),
        "maps": maps,
    }

    remaining_seconds = int(duration_min) * 60

    return render_template(
        "quiz/take_quiz.html",
        subject=subject,
        record_id=record.id,
        questions=q_compact,
        remaining_seconds=remaining_seconds,
    )


@bp.route('/submit', methods=['POST'])
@login_required
def submit_quiz():
    from datetime import datetime, timedelta

    record_id = request.form.get("record_id", type=int)
    if not record_id:
        abort(400, description="Missing record_id")

    record = QuizRecord.query.get_or_404(record_id)
    if record.user_id != g.user.id:
        abort(403)

    quiz_key = _quiz_session_key(record.id)
    data = session.get(quiz_key)
    if not data:
        flash("Quiz session expired or already submitted.", "danger")
        return redirect(url_for("quiz.select"))

    duration_min = int(data.get("duration_min", 15))
    try:
        start_utc = datetime.fromisoformat(data["start_utc"])
    except Exception:
        start_utc = record.start_time or datetime.utcnow()

    maps = data.get("maps") or {}
    score = 0

    answer_attr_name = None
    for name in ("chosen", "answer", "selected", "selected_option", "user_answer"):
        if hasattr(QuizAnswer, name):
            answer_attr_name = name
            break

    has_correct_col = hasattr(QuizAnswer, "correct")

    for qid_str, mapping in maps.items():
        qid = int(qid_str)
        chosen = request.form.get(f"q_{qid}")
        correct = mapping.get("correct")
        is_correct = (chosen == correct) if chosen else False
        if is_correct:
            score += 1

        ans = QuizAnswer(
            quiz_record_id=record.id,
            question_id=qid,
            is_correct=is_correct,
        )
        if answer_attr_name:
            setattr(ans, answer_attr_name, chosen)
        if has_correct_col:
            setattr(ans, "correct", correct)

        db.session.add(ans)

    record.end_time = datetime.utcnow()
    record.score = score
    db.session.commit()

    session.pop(quiz_key, None)
    if session.get('quiz_record_id') == record_id:
        session.pop('quiz_record_id', None)
    session.pop('current_qids', None)
    session.pop('quiz_locked', None)
    session.pop('quiz_duration_min', None)

    return redirect(url_for('quiz.result', record_id=record.id))


@bp.route('/result/<int:record_id>')
@login_required
def result(record_id):
    record = QuizRecord.query.get_or_404(record_id)
    if record.user_id != g.user.id:
        abort(403)

    answers = (
      db.session.query(QuizAnswer)
      .filter(QuizAnswer.quiz_record_id == record_id)
      .join(Question, Question.id == QuizAnswer.question_id)
      .options(db.contains_eager(QuizAnswer.question))
      .all()
    )

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


@bp.route("/leaderboard/<int:subject_id>")
def leaderboard(subject_id: int):
    subject = Subject.query.get_or_404(subject_id)
    rows = (
        db.session.query(QuizRecord, User)
        .join(User, User.id == QuizRecord.user_id)
        .filter(QuizRecord.subject_id == subject_id)
        .order_by(desc(QuizRecord.score), QuizRecord.end_time.desc())
        .limit(20)
        .all()
    )
    return render_template("quiz/leaderboard.html", subject=subject, rows=rows)
