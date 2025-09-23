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

