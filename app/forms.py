from operator import length_hint
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, RadioField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email
from app.models import Subject
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('<PASSWORD>', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class AddSubjectForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Add Subject')
    def validate_name(self, name):
        subject = Subject.query.filter_by(name=name.data).first()
        if subject is not None:
            raise ValidationError('That subject already exists.')

class AddQuestionForm(FlaskForm):
    subject_id = SelectField('Subject ID', validators=[DataRequired()])
    content = StringField('Question', validators=[DataRequired()])
    option_a = StringField('Option A', validators=[DataRequired()])
    option_b = StringField('Option B', validators=[DataRequired()])
    option_c = StringField('Option C', validators=[DataRequired()])
    option_d = StringField('Option D', validators=[DataRequired()])

    correct_answer = RadioField('Correct Answer', choices=[
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D')
    ], validators=[DataRequired()])

    submit = SubmitField('Add Question')