from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import SQLAlchemySessionUserDatastore, Security
from flask_login import LoginManager
from werkzeug.security import generate_password_hash


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.new_quiz_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'abcxyz'

db = SQLAlchemy(app)

from app import routes