from flask import render_template, g
from . import bp
from ...models import QuizRecord, Subject, User
from ...utils.auth import login_required

@bp.route('/')
def home():
    return render_template('main/index.html')

@bp.route('/history')
@login_required
def history():
    records = QuizRecord.query.filter_by(user_id=g.user.id).order_by(QuizRecord.id.desc()).all()
    return render_template('main/history.html', quiz_records=records)

@bp.route('/leaderboard/<int:subject_id>')
@login_required
def leaderboard(subject_id):
    records = QuizRecord.query.filter_by(subject_id=subject_id).order_by(
        QuizRecord.score.desc(), QuizRecord.end_time.desc()).limit(50).all()
    subject = Subject.query.get(subject_id)
    data = [{
        "username": User.query.get(r.user_id).username,
        "score": r.score,
        "end_time": r.end_time
    } for r in records]
    return render_template('shared/leaderboard.html', leaderboard_data=data, subject_name=subject.name if subject else "N/A")
