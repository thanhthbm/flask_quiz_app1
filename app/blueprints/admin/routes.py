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
