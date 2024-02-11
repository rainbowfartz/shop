from wtforms import *
from wtforms.fields import EmailField, DateField
from flask import *

class CreateUserForm(Form):
    Full_name = StringField('Full_name', [validators.Length(min=1, max=150), validators.DataRequired()])


class CreateCustomerForm(Form):
    Full_name = StringField('Full_name', [validators.Length(min=1, max=150), validators.DataRequired()])
    email = EmailField('Email', [validators.Email(), validators.DataRequired()])


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    
class LoginForm(Form):
    Email = StringField('Email', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.Length(min=6, max=80)])
