# Local imports
import datetime

# External imports
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, DateField, DecimalField
from wtforms.validators import DataRequired, Length, Optional
from wtforms_components import DateTimeField, DateRange

class PaymentForm(FlaskForm):
    """Flask Payment Form"""

    # Field types followed by label and data validators
    CreditCardNumber = StringField(
            'Credit Card Number',
            [
                DataRequired(),
                Length(min=13, max=16, message="Invalid Credit Card Number")
            ]
        )
    CardHolder = StringField(
            'Credit Card Holder',
            [
            DataRequired(),
            Length(min=5,max=49, message="Invalid Length")
            ]
        )
    ExpirationDate = DateField( 'Expiry Date (YYYY-MM-DD)',
            [
            DataRequired(),
            DateRange(
                min=datetime.datetime.today().date(),
                max=datetime.date(2030, 12, 31)
            )
            ],
            format='%Y-%m-%d'
        )

    SecurityCode = StringField('Security Code',
            [
            Optional(),
            Length(min=3, max=3, message="Length should be 3 digits")
            ]
        )

    Amount = DecimalField( 'Amount',
            [
            DataRequired()
            ],
            places=2
        )

    submit = SubmitField('Submit')