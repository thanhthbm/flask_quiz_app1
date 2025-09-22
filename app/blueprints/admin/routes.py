from flask import render_template, request, redirect, url_for, flash
from . import bp
from ...models import Subject
from ...extensions import db
from ...utils.auth import requires_roles
from ...utils.parsing import allowed_file, parse_uploaded_file, save_questions

@bp.route('/subjects', methods=['GET', 'POST'])
@requires_roles('admin')
def subjects():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Subject name is required', 'danger')
        elif Subject.query.filter_by(name=name).first():
            flash('Subject already exists', 'danger')
        else:
            db.session.add(Subject(name=name))
            db.session.commit()
            flash('Subject added', 'success')
            return redirect(url_for('admin.subjects'))
    return render_template('admin/subjects.html', subjects=Subject.query.all())

@bp.route('/questions/add', methods=['GET', 'POST'])
@requires_roles('admin')
def add_question():
    subjects = Subject.query.all()
    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        input_method = request.form.get('input_method', 'manual')
        if not subject_id:
            flash('Please select a subject.', 'danger')
            return render_template('admin/add_question.html', subjects=subjects)

        if input_method == 'manual':
            row = {
                'content': request.form.get('content', ''),
                'option_a': request.form.get('option_a', ''),
                'option_b': request.form.get('option_b', ''),
                'option_c': request.form.get('option_c', ''),
                'option_d': request.form.get('option_d', ''),
                'correct_answer': request.form.get('correct_answer', '')
            }
            if not all(row.values()):
                flash('Please fill all fields.', 'danger')
            else:
                save_questions([row], int(subject_id))
                flash('Question added.', 'success')
                return redirect(url_for('admin.add_question'))

        else:  # file upload
            file = request.files.get('file')
            if not file or not allowed_file(file.filename):
                flash('Invalid or missing file (.txt, .csv, .json only)', 'danger')
                return render_template('admin/add_question.html', subjects=subjects)

            rows = parse_uploaded_file(file)
            if not rows:
                flash('No valid questions found in file.', 'danger')
            else:
                save_questions(rows, int(subject_id))
                flash(f'{len(rows)} questions imported.', 'success')
                return redirect(url_for('admin.add_question'))

    return render_template('admin/add_question.html', subjects=subjects)
