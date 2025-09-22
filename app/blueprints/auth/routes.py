from flask import render_template, request, redirect, url_for, flash, session
from . import bp
from ...extensions import db
from ...models import User

@bp.route('/login', methods=['GET','POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password','')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = user.role
            flash('Logged in!', 'success')
            return redirect(url_for('main.home'))
        flash('Invalid username or password', 'danger')
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET','POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password','')
        if not username or not password:
            flash('Please fill all fields', 'danger')
        elif User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
        else:
            u = User(username=username)
            u.set_password(password)
            db.session.add(u)
            db.session.commit()
            flash('Registered successfully. Please login.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'success')
    return redirect(url_for('auth.login'))
