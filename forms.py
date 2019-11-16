from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from models import User
from database import DB

class Login(FlaskForm):
    username = StringField('Username', validators=[DataRequired()]) # cant submit empty field
    password = PasswordField('Password', validators=[DataRequired()]) # cant submit empty field
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    #email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = DB.find_one("users", {"username": str(username)})
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = DB.find_one("users", {"email": str(email)})
        if user is not None:
            raise ValidationError('Please use a different email address.')