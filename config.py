import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
    QUESTION_PER_PAGE = 1

    WTF_CSRF_ENABLED = False

    #Flask-User setting
    USER_APP_NAME = 'Quiz app'
    USER_ENABLE_EMAIL = True
    USER_ENABLE_USERNAME = False
    USER_ENABLE_PASSWORD_CHANGE = True
    USER_EMAIL_SENDER_NAME = USER_APP_NAME
    USER_EMAIL_SENDER_EMAIL = "thanhthbm@gmail.com"
