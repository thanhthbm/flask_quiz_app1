import os
import datetime
from flask import Flask, request, render_template_string
from flask_babelex import Babel
from sqlalchemy import SQLAlchemy
from flask_user import current_user, login_required, roles_required, UserMixin, UserManager
class Config:
    SECRET_KEY = 'abcxyz'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///quiz_app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'app/uploads'
    QUESTION_PER_PAGE = 1

    #Flask-Mail SMTP server
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'thanhthbm@gmail.com'
    MAIL_PASSWORD = '20032004567'
    MAIL_DEFAULT_SENDER = '"Quiz app" <<EMAIL>>'

    #Flask-User setting
    USER_APP_NAME = 'Quiz app'
    USER_ENABLE_EMAIL = True
    USER_ENABLE_USERNAME = False
    USER_ENABLE_PASSWORD_CHANGE = True
    USER_EMAIL_SENDER_NAME = USER_APP_NAME
    USER_EMAIL_SENDER_EMAIL = "thanhthbm@gmail.com"
