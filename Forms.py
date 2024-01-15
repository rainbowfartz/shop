from wtforms import Form, StringField, RadioField, SelectField, TextAreaField, validators, IntegerField

class CreateCheckoutForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    address = TextAreaField('Address', [validators.Length(min=1, max=150), validators.DataRequired()])
    card_number = StringField('Card Number', [validators.Length(min=1, max=150), validators.DataRequired()])
    exp_month = StringField('Month', [validators.Length(min=1, max=12), validators.DataRequired()])
    exp_year = StringField('Year', [validators.DataRequired()])
    cvv = StringField('Cvv', [validators.DataRequired()])