from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import (
  StringField, PasswordField, SubmitField, SelectField, RadioField, FileField,
  IntegerField, TextAreaField
)
from wtforms.validators import DataRequired, EqualTo, ValidationError, \
  NumberRange, InputRequired, Optional

from app.models import Subject, User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
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
  input_method = SelectField('Input Method', choices=[
    ('manual', 'Manual'),
    ('file', 'File')
  ], default='manual', validators=[InputRequired()])

  subject_id = SelectField('Subject', coerce=int, validators=[InputRequired()])
  content = TextAreaField('Question', validators=[Optional()])
  option_a = StringField('Option A', validators=[Optional()])
  option_b = StringField('Option B', validators=[Optional()])
  option_c = StringField('Option C', validators=[Optional()])
  option_d = StringField('Option D', validators=[Optional()])
  correct_answer = StringField('Correct Answer (A/B/C/D)',
                               validators=[Optional()])
  file = FileField('Upload File', validators=[
    FileAllowed(['txt', 'csv', 'json'], 'Allowed formats: .txt, .csv, .json')
  ])
  submit = SubmitField('Save')


class QuizForm(FlaskForm):
    subject_id = SelectField('Subject', validators=[InputRequired()], coerce=int)
    number_of_questions = IntegerField(
        'Number of Questions',
        validators=[DataRequired(), NumberRange(min=1, message="The number of questions must be greater than 0.")]
    )
    submit = SubmitField('Start Quiz')
