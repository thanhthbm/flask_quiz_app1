from flask import render_template, request, redirect, url_for, flash
from . import bp
from ...models import Subject
from ...extensions import db
from ...utils.auth import requires_roles
from ...utils.parsing import allowed_file, parse_uploaded_file, save_questions
from ...forms import AddSubjectForm, AddQuestionForm

@bp.route('/subjects', methods=['GET', 'POST'])
@requires_roles('admin')
def subjects():
    form = AddSubjectForm()

    subjects = Subject.query.order_by(Subject.name.asc()).all()

    if form.validate_on_submit():
        name = form.name.data.strip()
        if Subject.query.filter_by(name=name).first():
            flash('Subject already exists', 'danger')
        else:
            db.session.add(Subject(name=name))
            db.session.commit()
            flash('Subject added', 'success')
            return redirect(url_for('admin.subjects'))

    return render_template('admin/subjects.html', form=form, subjects=subjects)


@bp.route('/questions/add', methods=['GET', 'POST'])
@requires_roles('admin')
def add_question():
    form = AddQuestionForm()

    subjects = Subject.query.order_by(Subject.name.asc()).all()
    form.subject_id.choices = [(s.id, s.name) for s in subjects]

    if form.validate_on_submit():
        subject_id = form.subject_id.data
        input_method = form.input_method.data

        if input_method == 'manual':
            row = {
                'content': form.content.data.strip(),
                'option_a': form.option_a.data.strip(),
                'option_b': form.option_b.data.strip(),
                'option_c': form.option_c.data.strip(),
                'option_d': form.option_d.data.strip(),
                'correct_answer': form.correct_answer.data  # 'A'/'B'/'C'/'D'
            }

            if not all(row.values()):
                flash('Please fill all fields.', 'danger')
                return render_template('admin/add_question.html', form=form)

            save_questions([row], subject_id)
            flash('Question added.', 'success')
            return redirect(url_for('admin.add_question'))

        file = form.file.data  # WTForms FileField
        if not file or not allowed_file(file.filename):
            flash('Invalid or missing file (.csv, .json only)', 'danger')
            return render_template('admin/add_question.html', form=form)

        try:
            rows = parse_uploaded_file(file)
        except Exception as e:
            flash(f'Cannot parse file: {e}', 'danger')
            return render_template('admin/add_question.html', form=form)

        if not rows:
            flash('No valid questions found in file.', 'danger')
            return render_template('admin/add_question.html', form=form)

        save_questions(rows, subject_id)
        flash(f'{len(rows)} questions imported.', 'success')
        return redirect(url_for('admin.add_question'))

    return render_template('admin/add_question.html', form=form)


from flask import request, render_template, redirect, url_for, flash
from sqlalchemy import or_, desc
from . import bp
from ...extensions import db
from ...models import Subject, Question
from ...utils.auth import requires_roles
from ...forms import EditQuestionForm

@bp.route('/questions', methods=['GET'])
@requires_roles('admin')
def questions_manage():
    # Lọc/ tìm kiếm/ phân trang
    page = request.args.get('page', default=1, type=int)
    q = request.args.get('q', default='', type=str).strip()
    subject_id = request.args.get('subject_id', type=int)
    show_deleted = request.args.get('deleted', default=0, type=int)  # 0: active, 1: deleted

    query = Question.query
    if show_deleted:
        query = query.filter(Question.is_deleted.is_(True))
    else:
        query = query.filter(Question.is_deleted.is_(False))

    if subject_id:
        query = query.filter(Question.subject_id == subject_id)

    if q:
        like = f"%{q}%"
        query = query.filter(or_(Question.content.ilike(like),
                                 Question.option_a.ilike(like),
                                 Question.option_b.ilike(like),
                                 Question.option_c.ilike(like),
                                 Question.option_d.ilike(like)))

    query = query.order_by(desc(Question.id))
    pagination = query.paginate(page=page, per_page=20, error_out=False)

    subjects = Subject.query.order_by(Subject.name.asc()).all()
    return render_template('admin/questions_manage.html',
                           pagination=pagination,
                           items=pagination.items,
                           subjects=subjects,
                           current_subject_id=subject_id,
                           q=q,
                           show_deleted=show_deleted)

@bp.route('/questions/<int:qid>/edit', methods=['GET','POST'])
@requires_roles('admin')
def question_edit(qid):
    item = Question.query.get_or_404(qid)
    form = EditQuestionForm(obj=item)
    subjects = Subject.query.order_by(Subject.name.asc()).all()
    form.subject_id.choices = [(s.id, s.name) for s in subjects]

    if form.validate_on_submit():
        item.subject_id = form.subject_id.data
        item.content = form.content.data.strip()
        item.option_a = form.option_a.data.strip()
        item.option_b = form.option_b.data.strip()
        item.option_c = form.option_c.data.strip()
        item.option_d = form.option_d.data.strip()
        item.correct_answer = form.correct_answer.data.strip().upper()
        db.session.commit()
        flash('Question updated.', 'success')
        return redirect(url_for('admin.questions_manage'))

    return render_template('admin/question_edit.html', form=form, item=item)

@bp.route('/questions/<int:qid>/delete', methods=['POST'])
@requires_roles('admin')
def question_delete(qid):
    item = Question.query.get_or_404(qid)
    if item.is_deleted:
        flash('Question already deleted.', 'warning')
    else:
        item.is_deleted = True
        db.session.commit()
        flash('Question deleted (soft).', 'success')
    return redirect(url_for('admin.questions_manage',
                            page=request.args.get('page', 1),
                            q=request.args.get('q',''),
                            subject_id=request.args.get('subject_id'),
                            deleted=request.args.get('deleted', 0)))

@bp.route('/questions/<int:qid>/restore', methods=['POST'])
@requires_roles('admin')
def question_restore(qid):
    item = Question.query.get_or_404(qid)
    if not item.is_deleted:
        flash('Question is active already.', 'warning')
    else:
        item.is_deleted = False
        db.session.commit()
        flash('Question restored.', 'success')
    return redirect(url_for('admin.questions_manage',
                            page=request.args.get('page', 1),
                            q=request.args.get('q',''),
                            subject_id=request.args.get('subject_id'),
                            deleted=1))

@bp.route('/questions/bulk', methods=['POST'])
@requires_roles('admin')
def questions_bulk():
    action = request.form.get('action')
    ids = request.form.getlist('ids', type=int)

    if not ids:
        flash('No items selected.', 'warning')
        return redirect(url_for('admin.questions_manage', **request.args))

    q = Question.query.filter(Question.id.in_(ids))

    if action == 'delete':
        count = 0
        for it in q:
            if not it.is_deleted:
                it.is_deleted = True
                count += 1
        db.session.commit()
        flash(f'Deleted {count} question(s).', 'success')

    elif action == 'restore':
        count = 0
        for it in q:
            if it.is_deleted:
                it.is_deleted = False
                count += 1
        db.session.commit()
        flash(f'Restored {count} question(s).', 'success')

    else:
        flash('Invalid bulk action.', 'danger')

    return redirect(url_for('admin.questions_manage', **request.args))