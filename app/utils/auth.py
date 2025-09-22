from functools import wraps
from flask import g, session, redirect, url_for, flash, request
from ..models import User

def load_logged_in_user():
    g.user = None
    uid = session.get('user_id')
    if uid:
        g.user = User.query.get(uid)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return wrapper

def requires_roles(*roles):
    def deco(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if g.user is None or g.user.role not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return wrapper
    return deco
