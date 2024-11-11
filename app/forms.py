from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, RadioField, FileField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired, EqualTo, ValidationError, NumberRange

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
    # Lựa chọn phương thức nhập liệu
    input_method = RadioField('Input Method', choices=[
        ('manual', 'Manual Entry'),
        ('file', 'Upload File')
    ], validators=[DataRequired()], default='manual')

    # Dropdown cho subject (môn học)
    subject_id = SelectField('Subject ID', validators=[DataRequired()])

    # Câu hỏi
    content = StringField('Question', validators=[DataRequired()])

    # Các lựa chọn câu trả lời
    option_a = StringField('Option A', validators=[DataRequired()])
    option_b = StringField('Option B', validators=[DataRequired()])
    option_c = StringField('Option C', validators=[DataRequired()])
    option_d = StringField('Option D', validators=[DataRequired()])

    # Câu trả lời đúng
    correct_answer = RadioField('Correct Answer', choices=[
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D')
    ], validators=[DataRequired()])

    # Lựa chọn file để upload nếu chọn phương thức upload file
    file = FileField('Upload File (CSV or JSON)', validators=[
        FileAllowed(['csv', 'json'], 'Only CSV or JSON files are allowed.')
    ])

    submit = SubmitField('Add Question')


class QuizForm(FlaskForm):
    subject_id = SelectField('Subject ID', validators=[DataRequired()])
    number_of_questions = IntegerField('Number of Questions', validators=[
        DataRequired(),
        NumberRange(min=1, message="The number of questions must be greater than 0.")
    ])
    submit = SubmitField('Start Quiz')