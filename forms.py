from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, IntegerField, SubmitField, SelectMultipleField
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired, URL, Email, EqualTo, NumberRange

class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class CategoryForm(FlaskForm):
    category_name = StringField('Category Title', validators=[DataRequired()])
    api_id = IntegerField("API Id")

class QuestionForm(FlaskForm):
    question_text = StringField('Question Text', validators=[DataRequired()])
    option1 = StringField('Option 1', validators=[DataRequired()])
    option2 = StringField('Option 2', validators=[DataRequired()])
    option3 = StringField('Option 3', validators=[DataRequired()])
    option4 = StringField('Option 4', validators=[DataRequired()])
    correct = SelectField('Correct Option No', choices=[(1,1),(2,2),(3,3),(4,4)],validators=[DataRequired()])

class PopulateForm(FlaskForm):
    quantity = IntegerField('No of question to be fetched', validators=[DataRequired(),NumberRange(min=10, max=50)])
    difficulty = SelectField("Choose Difficulty", choices=[('easy', 'Easy'),('medium','Medium'),('hard', 'Hard')])

class EmailForm(FlaskForm):
    subject = StringField("Subject",validators=[DataRequired()])
    content = CKEditorField("Content",validators=[DataRequired()])