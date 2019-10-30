from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class Login(FlaskForm):
    username = StringField('Username', validators=[DataRequired()]) # cant submit empty field
    password = PasswordField('Password', validators=[DataRequired()]) # cant submit empty field
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')