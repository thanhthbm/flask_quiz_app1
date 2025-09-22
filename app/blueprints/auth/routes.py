# app/blueprints/auth/routes.py
from urllib.parse import urlparse, urljoin

from flask import render_template, request, redirect, url_for, flash, session
from . import bp
from ...extensions import db
from ...models import User
from ...forms import LoginForm, RegistrationForm


def _is_safe_url(target: str) -> bool:
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (test_url.scheme in ("http", "https")) and (ref_url.netloc == test_url.netloc)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            flash('Invalid username or password', 'danger')
            return render_template('auth/login.html', form=form)

        if user.is_locked:
            flash('Your account is locked. Please contact admin.', 'warning')
            return render_template('auth/login.html', form=form)

        session['user_id'] = user.id
        session['role'] = user.role

        flash('Logged in!', 'success')

        next_url = request.args.get('next')
        if _is_safe_url(next_url):
            return redirect(next_url)
        return redirect(url_for('main.home'))

    return render_template('auth/login.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'):
        return redirect(url_for('main.home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('auth/register.html', form=form)

        u = User(username=username)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()

        flash('Registered successfully. Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@bp.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    flash('Logged out.', 'success')
    return redirect(url_for('auth.login'))
