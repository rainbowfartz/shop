from wtforms import Form, StringField, RadioField, SelectField, TextAreaField, validators
from wtforms.fields import EmailField, DateField

class CreateUserForm(Form):
    Full_name = StringField('Full_name', [validators.Length(min=1, max=150), validators.DataRequired()])


class CreateCustomerForm(Form):
    Full_name = StringField('Full_name', [validators.Length(min=1, max=150), validators.DataRequired()])
    email = EmailField('Email', [validators.Email(), validators.DataRequired()])
