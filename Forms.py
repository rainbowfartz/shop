from wtforms import Form, StringField, RadioField, SelectField, TextAreaField, validators, IntegerField

class CreateCheckoutForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=150), validators.Regexp(regex="[a-zA-Z]", message='Please enter letters only.'),validators.DataRequired()], render_kw={"placeholder":"John Lee"})
    address = TextAreaField('Address', [validators.Length(min=1, max=150),validators.Regexp(regex="[0-9-a-zA-Z]", message='Please enter address accordingly.'), validators.DataRequired()], render_kw={"placeholder":"100A Neighbourhood 01-010 100100"})
    card_number = StringField('Card Number', [validators.Length(min=1, max=150),validators.Regexp(regex="^(?:4[0-9]{12}(?:[0-9]{3})?|[25][1-7][0-9]{14}|6(?:011|5[0-9][0-9])[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|(?:2131|1800|35\d{3})\d{11})$", message='Please enter valid card number.'), validators.DataRequired()], render_kw={"placeholder":"1234123412341234"})
    exp_month = StringField('Month', [validators.Length(min=1, max=12),validators.Regexp(regex="^(0?[1-9]|1[012])$", message='Please enter valid month.'),validators.DataRequired()], render_kw={"placeholder":"mm"})
    exp_year = StringField('Year', [validators.Regexp(regex="^(19|20)\d{2}$", message='Please enter valid year.'),validators.DataRequired()], render_kw={"placeholder":"yyyy"})
    cvv = StringField('Cvv', [validators.Regexp(regex="^[0-9]{3,4}$", message='Please enter valid cvv.'),validators.DataRequired()], render_kw={"placeholder":"123"})

    #  validators.Regexp(regex="^[0-9]{3,4}$", message='Please enter valid cvv.')
    # validators.Regexp(regex="^(19|20)\d{2}$", message='Please enter valid year.'), render_kw={"placeholder":"yyyy"}
    # ,validators.Regexp(regex="^(0?[1-9]|1[012])$", message='Please enter valid month.'), validators.DataRequired()], render_kw={"placeholder":"mm"}